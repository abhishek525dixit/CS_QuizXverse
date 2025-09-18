(function(){
	if (!document.currentScript) return;
	const config = window.__QUIZ_CONFIG__ || null;
	const isQuizPage = !!config;
	if (!isQuizPage) return;

	const qContainer = document.getElementById('question-container');
	const optionsEl = document.getElementById('options');
	const timerEl = document.getElementById('timer');
	const progressEl = document.getElementById('progress');
	const prevBtn = document.getElementById('prevBtn');
	const nextBtn = document.getElementById('nextBtn');
	const finishBtn = document.getElementById('finishBtn');
	const barFill = document.getElementById('barFill');
	const hintBtn = document.getElementById('hintBtn');

	let questions = [];
	let currentIndex = 0;
	let answers = []; // {id, choice_index, time_spent}
	let quizTotalSeconds = Math.max(60, Math.floor(config.durationMinutes * 60));
	let quizTimerHandle = null;
	let perQuestionSeconds = 30; // default per-question timer
	let perQuestionRemaining = perQuestionSeconds;
	let perQTimerHandle = null;
	let liveScore = 0; // updated as user answers
    // Per-question hint usage is tracked on each question object as:
    // q.__hintUsed: boolean, q.__disabledOptions: Set<number>
    let totalHintsAllowed = 0; // total hints for the whole quiz
    let totalHintsUsed = 0;    // incremented once per question when hint used

	function updateProgress(){
		progressEl.textContent = `Question ${currentIndex+1}/${questions.length} • Score ${liveScore}`;
		const pct = ((currentIndex) / Math.max(1, questions.length)) * 100;
		barFill.style.width = pct + '%';
	}

	function renderQuestion(){
		if (!questions.length) return;
		const q = questions[currentIndex];
		qContainer.textContent = q.question;
		optionsEl.innerHTML = '';
        q.options.forEach((opt, idx)=>{
			const li = document.createElement('li');
			li.textContent = opt;
			li.tabIndex = 0;
			li.addEventListener('click', ()=> selectOption(idx));
			li.addEventListener('keypress', (e)=>{ if(e.key==='Enter') selectOption(idx); });
			if ((answers[currentIndex]||{}).choice_index === idx){ li.classList.add('selected'); }
            // Re-apply previously disabled options if a hint was used on this question
            if (q.__disabledOptions && q.__disabledOptions.has(idx)){
                li.classList.add('disabled');
                li.style.opacity = '0.5';
                li.style.pointerEvents = 'none';
            }
            optionsEl.appendChild(li);
		});
		prevBtn.disabled = currentIndex===0;
		nextBtn.disabled = currentIndex===questions.length-1;
        updateProgress();
        resetPerQuestionTimer();
        updateHintButton();
	}

	function applySpeedBonus(timeSpentSec, correct){
		// bonus: +1 extra point if answered within 10 seconds and correct
		if (correct && timeSpentSec <= 10) return 1;
		return 0;
	}

	function selectOption(idx){
		const timeSpent = perQuestionSeconds - perQuestionRemaining;
		answers[currentIndex] = { id: questions[currentIndex].id, choice_index: idx, time_spent: timeSpent };
		Array.from(optionsEl.children).forEach((li, i)=>{
			li.classList.toggle('selected', i===idx);
		});
		// Immediate live score check using answer key
		if (typeof questions[currentIndex].correct_index === 'number'){
			const wasCorrectBefore = questions[currentIndex].__wasCorrect || false;
			const isCorrectNow = idx === questions[currentIndex].correct_index;
			const delta = (isCorrectNow ? 1 : 0) - (wasCorrectBefore ? 1 : 0);
			let bonus = 0;
			if (!wasCorrectBefore && isCorrectNow){ bonus = applySpeedBonus(timeSpent, true); }
			liveScore += delta + bonus;
			questions[currentIndex].__wasCorrect = isCorrectNow;
			updateProgress();
		}
	}

	function tickQuiz(){
		const m = Math.floor(quizTotalSeconds/60).toString().padStart(2,'0');
		const s = (quizTotalSeconds%60).toString().padStart(2,'0');
		timerEl.textContent = `${m}:${s}`;
		if (quizTotalSeconds<=0){ submitAnswers(); return; }
		quizTotalSeconds -= 1;
	}

	function startQuizTimer(){
		if (quizTimerHandle) clearInterval(quizTimerHandle);
		quizTimerHandle = setInterval(tickQuiz, 1000);
		tickQuiz();
	}

	function tickPerQuestion(){
		perQuestionRemaining -= 1;
		if (perQuestionRemaining <= 0){
			handleNoAnswer();
			nextOrFinish();
		}
	}

	function resetPerQuestionTimer(){
		perQuestionRemaining = perQuestionSeconds;
		if (perQTimerHandle) clearInterval(perQTimerHandle);
		perQTimerHandle = setInterval(tickPerQuestion, 1000);
	}

	function handleNoAnswer(){
		if (!answers[currentIndex]){
			answers[currentIndex] = { id: questions[currentIndex].id, choice_index: -1, time_spent: perQuestionSeconds };
		}
	}

	function nextOrFinish(){
		if (currentIndex < questions.length-1){
			currentIndex += 1;
			renderQuestion();
		} else {
			submitAnswers();
		}
	}

    async function loadQuestions(){
        // Use Flask API endpoint
        const url = `/api/questions?subject=${encodeURIComponent(config.subject)}&count=${encodeURIComponent(config.count || 30)}`;
        const res = await fetch(url);
		const data = await res.json();
		questions = (data.questions || []).sort(()=> Math.random()-0.5);
		answers = new Array(questions.length).fill(null);
		currentIndex = 0;
		// Fetch answer key for live score
		const ids = questions.map(q=>q.id).join(',');
		try {
            const akRes = await fetch(`/api/answer_key?subject=${encodeURIComponent(config.subject)}&ids=${encodeURIComponent(ids)}`);
			const ak = await akRes.json();
			const map = ak.answers || {};
			questions.forEach(q=>{ if(map[q.id]) q.correct_index = map[q.id].correct_index; });
		} catch(e) {}
        liveScore = 0;
        // Total 50:50 hint budget = half of total questions (rounded down)
        totalHintsAllowed = Math.floor(questions.length / 2);
        totalHintsUsed = 0;
        updateHintButton();
		renderQuestion();
		startQuizTimer();
	}

    async function submitAnswers(){
		if (quizTimerHandle) clearInterval(quizTimerHandle);
		if (perQTimerHandle) clearInterval(perQTimerHandle);
		const filled = answers.map((a, i)=> a || { id: questions[i].id, choice_index: -1, time_spent: perQuestionSeconds });
        // Use Flask API endpoint
        const res = await fetch('/api/score',{
			method:'POST',
			headers:{'Content-Type':'application/json'},
            body: JSON.stringify({
                subject: config.subject,
                answers: filled
            })
		});
		const data = await res.json();
		const baseScore = data.score || 0;
		const total = questions.length;
		const speedBonus = filled.reduce((acc,a,i)=>{
			const correct = questions[i] && a.choice_index === questions[i].correct_index;
			return acc + (correct && a.time_spent <= 10 ? 1 : 0);
		}, 0);
		const finalScore = baseScore + speedBonus;
		const percentage = Math.round((finalScore / total) * 100);
		// Store detailed results in sessionStorage for results page
		sessionStorage.setItem('quiz_details', JSON.stringify({
			subject: config.subject,
			questions,
			answers: filled,
			serverDetails: data.details,
			finalScore,
			percentage
		}));
		location.href = `/results?score=${encodeURIComponent(finalScore)}&total=${encodeURIComponent(total)}`;
	}

    function updateHintButton(){
        const q = questions[currentIndex];
        const remaining = Math.max(0, totalHintsAllowed - totalHintsUsed);
        if (!q || typeof q.correct_index !== 'number'){
            hintBtn.textContent = `50-50 Hint (Unavailable, ${remaining} left)`;
            hintBtn.disabled = true;
            return;
        }
        const used = !!q.__hintUsed;
        const labelState = used ? 'Used' : 'Available';
        hintBtn.textContent = `50-50 Hint (${labelState}, ${remaining} left)`;
        hintBtn.disabled = used || remaining <= 0;
    }

    function useHint(){
        const q = questions[currentIndex];
        if (!q || typeof q.correct_index !== 'number') return;
        if (q.__hintUsed) return;
        const remaining = Math.max(0, totalHintsAllowed - totalHintsUsed);
        if (remaining <= 0) { updateHintButton(); return; }
        // Determine two wrong options to disable
        const wrongIndexes = q.options.map((_, i)=> i).filter(i=> i !== q.correct_index);
        // Shuffle and take first 2
        wrongIndexes.sort(()=> Math.random()-0.5);
        const toDisable = new Set(wrongIndexes.slice(0, 2));
        q.__disabledOptions = toDisable;
        q.__hintUsed = true;
        totalHintsUsed += 1;
        // Apply to DOM
        Array.from(optionsEl.children).forEach((li, idx)=>{
            if (toDisable.has(idx)){
                li.classList.add('disabled');
                li.style.opacity = '0.5';
                li.style.pointerEvents = 'none';
            }
        });
        updateHintButton();
    }

	prevBtn.addEventListener('click', ()=>{ if(currentIndex>0){ currentIndex--; renderQuestion(); }});
	nextBtn.addEventListener('click', ()=>{ handleNoAnswer(); nextOrFinish(); });
	finishBtn.addEventListener('click', ()=> submitAnswers());
	hintBtn.addEventListener('click', ()=> useHint());

	// Allow customizing per-question time via URL: &perq=SECONDS
	const sp = new URLSearchParams(location.search);
	perQuestionSeconds = Math.max(5, Number(sp.get('perq')||30));

	loadQuestions();
})();

