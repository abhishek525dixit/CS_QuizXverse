#!/usr/bin/env python3
"""
Build script for Netlify deployment.
This script generates static files and prepares the project for deployment.
"""

import json
import os
import shutil
from pathlib import Path
from flask import Flask, render_template

# Import your app configuration
import sys
sys.path.append('.')
from app import app, QUESTIONS_BY_SUBJECT, SUPPORTED_SUBJECTS

def build_static_site():
    """Build static files for Netlify deployment."""
    
    # Create dist directory
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copy static files
    static_dir = Path("static")
    if static_dir.exists():
        shutil.copytree(static_dir, dist_dir / "static", dirs_exist_ok=True)
    
    # Copy data directory
    data_dir = Path("data")
    if data_dir.exists():
        shutil.copytree(data_dir, dist_dir / "data", dirs_exist_ok=True)
    
    # Copy templates
    src_templates = Path("templates")
    if src_templates.exists():
        templates_dir = dist_dir / "templates"
        shutil.copytree(src_templates, templates_dir, dirs_exist_ok=True)
    
    # Generate static HTML files
    with app.test_client() as client:
        # Home page
        response = client.get('/')
        if response.status_code == 200:
            (dist_dir / "index.html").write_text(response.data.decode('utf-8'))
        
        # Quiz pages for each subject
        for subject in SUPPORTED_SUBJECTS:
            response = client.get(f'/quiz/{subject}')
            if response.status_code == 200:
                (dist_dir / f"quiz_{subject}.html").write_text(response.data.decode('utf-8'))
        
        # Results page
        response = client.get('/results')
        if response.status_code == 200:
            (dist_dir / "results.html").write_text(response.data.decode('utf-8'))
    
    # Generate API data files
    api_dir = dist_dir / "api"
    api_dir.mkdir()
    
    # Generate questions data for each subject
    for subject in SUPPORTED_SUBJECTS:
        questions = QUESTIONS_BY_SUBJECT.get(subject, [])
        public_questions = [
            {
                "id": q["id"], 
                "question": q["question"], 
                "options": q["options"]
            }
            for q in questions
        ]
        
        # Write questions file
        questions_file = api_dir / f"questions_{subject}.json"
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump({"questions": public_questions}, f, indent=2)
    
    # Generate subjects data
    subjects_data = {
        "subjects": SUPPORTED_SUBJECTS,
        "counts": {s: len(QUESTIONS_BY_SUBJECT.get(s, [])) for s in SUPPORTED_SUBJECTS}
    }
    
    subjects_file = api_dir / "subjects.json"
    with open(subjects_file, 'w', encoding='utf-8') as f:
        json.dump(subjects_data, f, indent=2)
    
    print(f"✅ Static site built successfully in {dist_dir}")
    print(f"📁 Generated files:")
    for file_path in dist_dir.rglob("*"):
        if file_path.is_file():
            print(f"   - {file_path.relative_to(dist_dir)}")

if __name__ == "__main__":
    build_static_site()
