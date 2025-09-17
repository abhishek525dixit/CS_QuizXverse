# Question bank

Place JSON files in `data/questions/` named after each subject key: `python.json`, `c.json`, `html.json`, `css.json`, `javascript.json`, `java.json`.

Each file should be a JSON array. Each item must have:

- `id` (string or number): unique per subject
- `question` (string)
- `options` (array of 2-8 strings)
- `answer_index` (number; 0-based index into `options`)

Example item:
```json
{
  "id": 101,
  "question": "Which keyword defines a function in Python?",
  "options": ["func", "def", "function", "lambda"],
  "answer_index": 1
}
```

Tips:
- Include at least 100 questions per subject for a full bank.
- IDs can be sequential numbers or meaningful codes.
- Keep options concise; avoid trick wording.
- Validate JSON format to prevent load errors.


