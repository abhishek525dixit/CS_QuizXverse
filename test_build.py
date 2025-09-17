#!/usr/bin/env python3
"""
Test script to verify the build process works correctly.
"""

import os
import sys
import json
from pathlib import Path

def test_build():
    """Test the build process."""
    print("🧪 Testing CS Quizverse build process...")
    
    # Check if required files exist
    required_files = [
        'app.py',
        'build.py', 
        'netlify.toml',
        'requirements.txt',
        'package.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    
    # Check if data directory exists
    if not Path('data/questions').exists():
        print("❌ Data directory missing")
        return False
    
    print("✅ Data directory exists")
    
    # Check if at least one question file exists
    question_files = list(Path('data/questions').glob('*.json'))
    if not question_files:
        print("❌ No question files found")
        return False
    
    print(f"✅ Found {len(question_files)} question files")
    
    # Test importing the app
    try:
        import app
        print("✅ App imports successfully")
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False
    
    # Test running the build script
    try:
        import build
        print("✅ Build script imports successfully")
    except Exception as e:
        print(f"❌ Build script import failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Your project is ready for Netlify deployment.")
    print("\nNext steps:")
    print("1. Push your code to a Git repository")
    print("2. Connect the repository to Netlify")
    print("3. Set build command: python build.py")
    print("4. Set publish directory: dist")
    print("5. Deploy!")
    
    return True

if __name__ == "__main__":
    success = test_build()
    sys.exit(0 if success else 1)
