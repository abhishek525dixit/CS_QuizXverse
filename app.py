import json
import os
import random
from pathlib import Path

from flask import Flask, jsonify, render_template, request, abort

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "questions"

app = Flask(__name__)

# Load questions for all subjects into memory
QUESTIONS_BY_SUBJECT = {}
SUPPORTED_SUBJECTS = [
	"python",
	"c",
	"html",
	"css",
	"javascript",
	"java",
]


def load_questions() -> None:
	DATA_DIR.mkdir(parents=True, exist_ok=True)
	for subject in SUPPORTED_SUBJECTS:
		file_path = DATA_DIR / f"{subject}.json"
		if not file_path.exists():
			QUESTIONS_BY_SUBJECT[subject] = []
			continue
		with open(file_path, "r", encoding="utf-8") as f:
			try:
				data = json.load(f)
			except json.JSONDecodeError:
				data = []
		# Normalize structure and ensure required keys
		normalized = []
		for item in data:
			if not all(k in item for k in ("id", "question", "options", "answer_index")):
				continue
			if not isinstance(item["options"], list) or len(item["options"]) < 2:
				continue
			normalized.append({
				"id": str(item["id"]),
				"question": str(item["question"]),
				"options": [str(opt) for opt in item["options"]],
				"answer_index": int(item["answer_index"]),
			})
		QUESTIONS_BY_SUBJECT[subject] = normalized


load_questions()


@app.route("/")
def home():
	subjects = [
		{"key": s, "label": s.capitalize()} for s in SUPPORTED_SUBJECTS
	]
	return render_template("index.html", subjects=subjects)


@app.route("/quiz/<subject>")
def quiz(subject: str):
	subject = subject.lower()
	if subject not in SUPPORTED_SUBJECTS:
		abort(404)
	return render_template("quiz.html", subject=subject, subject_label=subject.capitalize())


@app.route("/results")
def results_page():
	return render_template("result.html")


@app.get("/api/subjects")
def get_subjects():
	return jsonify({
		"subjects": SUPPORTED_SUBJECTS,
		"counts": {s: len(QUESTIONS_BY_SUBJECT.get(s, [])) for s in SUPPORTED_SUBJECTS},
	})

@app.get("/api/questions")
def get_questions():
	subject = request.args.get("subject", type=str, default="").lower()
	# Enforce fixed quiz length of 50 per subject (or fewer if pool smaller)
	if subject not in SUPPORTED_SUBJECTS:
		return jsonify({"error": "Unsupported subject"}), 400
	pool = QUESTIONS_BY_SUBJECT.get(subject, [])
	if not pool:
		return jsonify({"questions": []})
	count = max(1, min(50, len(pool)))
	selected = random.sample(pool, count)
	public_questions = [
		{"id": q["id"], "question": q["question"], "options": q["options"]}
		for q in selected
	]
	return jsonify({"questions": public_questions})


@app.get("/api/answer_key")
def get_answer_key():
	subject = request.args.get("subject", type=str, default="").lower()
	ids_csv = request.args.get("ids", type=str, default="")
	if subject not in SUPPORTED_SUBJECTS:
		return jsonify({"error": "Unsupported subject"}), 400
	ids = [i.strip() for i in ids_csv.split(",") if i.strip()]
	answers = {}
	for q in QUESTIONS_BY_SUBJECT.get(subject, []):
		if q["id"] in ids:
			answers[q["id"]] = {
				"correct_index": q["answer_index"],
				"correct_text": q["options"][q["answer_index"]],
			}
	return jsonify({"answers": answers})


@app.post("/api/score")
def submit_score():
	payload = request.get_json(silent=True) or {}
	subject = str(payload.get("subject", "")).lower()
	answers = payload.get("answers", [])
	# answers: list of { id: string, choice_index: int }
	if subject not in SUPPORTED_SUBJECTS:
		return jsonify({"error": "Unsupported subject"}), 400
	answer_key = {q["id"]: q["answer_index"] for q in QUESTIONS_BY_SUBJECT.get(subject, [])}
	score = 0
	details = []
	for ans in answers:
		qid = str(ans.get("id"))
		choice_index = int(ans.get("choice_index", -1))
		correct_index = answer_key.get(qid, None)
		if correct_index is None:
			continue
		is_correct = choice_index == correct_index
		if is_correct:
			score += 1
		details.append({
			"id": qid,
			"choice_index": choice_index,
			"correct_index": correct_index,
			"is_correct": is_correct,
		})
	return jsonify({
		"score": score,
		"total": len(answers),
		"details": details,
	})


if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)

