# The CS_QuizXverse

A modern quiz web app built with Flask (Python) and a lightweight HTML/CSS/JS frontend. Each section (Python, C, Java, JavaScript, HTML, CSS) has 50 multiple-choice questions, timers, a per-question 50:50 hint, and a detailed results review.

## Features

- Fixed 50 questions per section
- Overall quiz timer and per-question timer
- Real-time scoring feedback while selecting
- 50:50 Hint per question (one-time), shows remaining hints
- Results page with score and full answer breakdown
- Dark/Light theme toggle (persists)
- Flask-only backend (no Netlify)

## Tech Stack

- Backend: Flask (Python)
- Frontend: HTML, CSS, Vanilla JavaScript
- Data: JSON files under `data/questions/`

## Getting Started

Windows PowerShell:

```
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

## Project Structure

```
CS_Quizverse/
├─ app.py
├─ data/questions/*.json
├─ static/css/style.css
├─ static/js/quiz.js
├─ templates/base.html
├─ templates/index.html
├─ templates/quiz.html
└─ templates/result.html
```

## API (Flask)

- GET `/api/questions?subject=<key>` → up to 50 questions
- GET `/api/answer_key?subject=<key>&ids=<id1,id2,...>` → correct indexes
- POST `/api/score` with `{ subject, answers: [{ id, choice_index, time_spent }] }` → `{ score, total, details }`

## Question JSON Format

```
{
  "id": "unique-id",
  "question": "Text?",
  "options": ["A","B","C","D"],
  "answer_index": 2
}
```

## Founder

- Abhishek Dixit
- Email: abhishekd0999@gmail.com
- GitHub: https://github.com/Abhishek525dixit
- LinkedIn: https://www.linkedin.com/in/abhishek-dixit-056887350
- Site: The CS_QuizXverse — "Level up your Coding skills with fun with Braining quizzes to sharp your mind."

## Notes

- Rewards and leaderboards removed per latest requirements.
- Netlify config removed; runs purely on Flask.

