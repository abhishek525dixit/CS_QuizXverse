"""
Netlify Function for handling questions API endpoints.
"""

import json
import random
import os
from pathlib import Path

# Load questions data
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "questions"

SUPPORTED_SUBJECTS = [
    "python",
    "c", 
    "html",
    "css",
    "javascript",
    "java",
]

QUESTIONS_BY_SUBJECT = {}

def load_questions():
    """Load questions for all subjects into memory."""
    global QUESTIONS_BY_SUBJECT
    
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

# Load questions on import
load_questions()

def handler(event, context):
    """Handle the Netlify function request."""
    
    # Parse the request
    http_method = event.get('httpMethod', 'GET')
    query_params = event.get('queryStringParameters') or {}
    path = event.get('path', '')
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    # Handle OPTIONS request for CORS
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Handle different actions based on query parameters and HTTP method
        action = query_params.get('action', '')
        
        if http_method == 'GET':
            if action == 'answer_key':
                return handle_answer_key(query_params, headers)
            elif action == 'subjects':
                return handle_subjects(headers)
            else:
                return handle_questions(query_params, headers)
        elif http_method == 'POST':
            # Parse body for POST requests
            try:
                body_data = json.loads(event.get('body', '')) if event.get('body') else {}
                action = body_data.get('action', '')
            except json.JSONDecodeError:
                body_data = {}
            
            if action == 'score':
                return handle_score(event.get('body', ''), headers)
            else:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid action for POST request'})
                }
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def handle_questions(query_params, headers):
    """Handle questions endpoint."""
    subject = query_params.get('subject', '').lower()
    count = int(query_params.get('count', 30))
    
    if subject not in SUPPORTED_SUBJECTS:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Unsupported subject'})
        }
    
    pool = QUESTIONS_BY_SUBJECT.get(subject, [])
    if not pool:
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'questions': []})
        }
    
    count = max(1, min(count, len(pool)))
    selected = random.sample(pool, count)
    
    public_questions = [
        {
            'id': q['id'],
            'question': q['question'],
            'options': q['options']
        }
        for q in selected
    ]
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'questions': public_questions})
    }

def handle_subjects(headers):
    """Handle subjects endpoint."""
    subjects_data = {
        'subjects': SUPPORTED_SUBJECTS,
        'counts': {s: len(QUESTIONS_BY_SUBJECT.get(s, [])) for s in SUPPORTED_SUBJECTS}
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(subjects_data)
    }

def handle_answer_key(query_params, headers):
    """Handle answer key endpoint."""
    subject = query_params.get('subject', '').lower()
    ids_csv = query_params.get('ids', '')
    
    if subject not in SUPPORTED_SUBJECTS:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Unsupported subject'})
        }
    
    ids = [i.strip() for i in ids_csv.split(',') if i.strip()]
    answers = {}
    
    for q in QUESTIONS_BY_SUBJECT.get(subject, []):
        if q['id'] in ids:
            answers[q['id']] = {
                'correct_index': q['answer_index'],
                'correct_text': q['options'][q['answer_index']],
            }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'answers': answers})
    }

def handle_score(body, headers):
    """Handle score submission endpoint."""
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    
    subject = str(payload.get('subject', '')).lower()
    answers = payload.get('answers', [])
    
    if subject not in SUPPORTED_SUBJECTS:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Unsupported subject'})
        }
    
    answer_key = {q['id']: q['answer_index'] for q in QUESTIONS_BY_SUBJECT.get(subject, [])}
    score = 0
    details = []
    
    for ans in answers:
        qid = str(ans.get('id'))
        choice_index = int(ans.get('choice_index', -1))
        correct_index = answer_key.get(qid, None)
        
        if correct_index is None:
            continue
        
        is_correct = choice_index == correct_index
        if is_correct:
            score += 1
        
        details.append({
            'id': qid,
            'choice_index': choice_index,
            'correct_index': correct_index,
            'is_correct': is_correct,
        })
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'score': score,
            'total': len(answers),
            'details': details,
        })
    }
