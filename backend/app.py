"""
app.py
======
Flask backend — main server file।
Frontend থেকে CV upload এলে parse করে MySQL এ save করে।

Run:
    python app.py
"""

import os
import logging
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

from config import DEBUG, PORT, HOST, SECRET_KEY, UPLOAD_FOLDER, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, GEMINI_API_KEY
from cv_parser import CVParser
from db_manager import DBManager

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ── Flask App ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# CORS — frontend থেকে call আসতে দেবে
CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*', 'null'])

# Upload folder তৈরি করো যদি না থাকে
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Global Instances ──────────────────────────────────────────────────────────
cv_parser = CVParser()
db = DBManager()
db.init_tables()  # প্রথমবার সব tables তৈরি করবে


# ── Helper: allowed file type check ──────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


# ── Helper: get user_id from token (placeholder — তোমার auth দিয়ে replace করো) ──
def get_user_id_from_request() -> int:
    """
    Authorization header থেকে user_id বের করে।
    এখন এটা একটা simple placeholder।
    তুমি JWT বা session দিয়ে implement করবে।
    """
    auth = request.headers.get('Authorization', '')
    # Example: "Bearer user_id:5"  (development only)
    if 'user_id:' in auth:
        try:
            return int(auth.split('user_id:')[1].strip())
        except Exception:
            pass
    return 1  # Default to user_id=1 for testing


# ════════════════════════════════════════════════════════════════════════════════
# ── Route: POST /api/cv/upload ────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════════

@app.route('/api/cv/upload', methods=['POST'])
def upload_cv():
    """
    Frontend থেকে CV file upload করলে এই route call হয়।

    Request:
        multipart/form-data
        - cv: file (PDF / DOCX / TXT)

    Response (JSON):
        {
          "success": true,
          "cv_id": 12,
          "message": "CV uploaded and saved successfully.",
          "data": { ...extracted fields... }
        }
    """
    # ── 1. File validation ─────────────────────────────────────────────────
    if 'cv' not in request.files:
        return jsonify({'success': False, 'error': 'No CV file provided.'}), 400

    file = request.files['cv']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Empty filename.'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'File type not allowed. Use: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 415

    # ── 2. Read file bytes ─────────────────────────────────────────────────
    file_bytes = file.read()
    file_size_kb = len(file_bytes) / 1024
    filename = file.filename
    user_id = get_user_id_from_request()

    logger.info(f"📄 CV upload received: {filename} ({file_size_kb:.1f} KB) from user_id={user_id}")

    # ── 3. Parse CV ────────────────────────────────────────────────────────
    try:
        cv_data = cv_parser.parse(file_bytes=file_bytes, filename=filename)
        logger.info(f"✅ CV parsed: name='{cv_data.get('name')}', skills count={len(cv_data.get('skills', []))}")
    except Exception as e:
        logger.error(f"CV parsing failed: {e}")
        return jsonify({'success': False, 'error': f'CV parsing failed: {str(e)}'}), 500

    # ── 4. Save to MySQL ───────────────────────────────────────────────────
    try:
        cv_id = db.save_cv_data(
            user_id=user_id,
            cv_data=cv_data,
            filename=filename,
            file_size_kb=file_size_kb
        )
        logger.info(f"✅ CV data saved to DB. cv_id={cv_id}")
    except Exception as e:
        logger.error(f"DB save failed: {e}")
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500

    # ── 5. Return extracted data (raw_text বাদে) ───────────────────────────
    response_data = {k: v for k, v in cv_data.items() if k != 'raw_text'}

    return jsonify({
        'success' : True,
        'cv_id'   : cv_id,
        'message' : 'CV uploaded and all data saved successfully.',
        'data'    : response_data
    }), 201


# ════════════════════════════════════════════════════════════════════════════════
# ── Route: POST /api/interview/start ─────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════════

@app.route('/api/interview/start', methods=['POST'])
def start_interview():
    """
    Frontend থেকে CV + selected field এলে:
    1. CV parse করে MySQL এ save করে
    2. Gemini দিয়ে interview questions generate করে

    Request:
        multipart/form-data
        - cv: file
        - field: string (e.g., "Data Science")

    Response:
        { "questions": [{id, question, difficulty}, ...] }
    """
    import google.generativeai as genai  # pip install google-generativeai

    # ── Validate ────────────────────────────────────────────────────────────
    if 'cv' not in request.files:
        return jsonify({'error': 'CV file is required.'}), 400

    file = request.files['cv']
    field = request.form.get('field', 'General')

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid CV file.'}), 400

    # ── Parse & Save CV ─────────────────────────────────────────────────────
    file_bytes = file.read()
    file_size_kb = len(file_bytes) / 1024
    user_id = get_user_id_from_request()

    try:
        cv_data = cv_parser.parse(file_bytes=file_bytes, filename=file.filename)
        cv_id = db.save_cv_data(
            user_id=user_id,
            cv_data=cv_data,
            filename=file.filename,
            file_size_kb=file_size_kb
        )
    except Exception as e:
        return jsonify({'error': f'CV processing failed: {str(e)}'}), 500

    # ── Build Gemini Prompt ────────────────────────────────────────────────
    skills_str = ', '.join(cv_data.get('skills', [])[:20]) or 'Not found'
    edu_str = '; '.join(
        f"{e.get('degree', '')} from {e.get('institution', '')}"
        for e in cv_data.get('education', [])[:3]
    ) or 'Not found'
    exp_str = '; '.join(
        f"{e.get('title', '')} at {e.get('company', '')}"
        for e in cv_data.get('experience', [])[:3]
    ) or 'Not found'

    prompt = f"""You are an expert technical interviewer. Based on the following candidate profile, generate exactly 5 interview questions for the field: {field}.

CANDIDATE PROFILE:
- Name: {cv_data.get('name', 'Candidate')}
- Skills: {skills_str}
- Education: {edu_str}
- Experience: {exp_str}
- Summary: {cv_data.get('summary', '')[:500]}

REQUIREMENTS:
- Questions must be specific to the candidate's skills and the "{field}" field.
- Mix of difficulties: 2 Easy, 2 Medium, 1 Hard.
- Return ONLY a JSON array (no markdown, no explanation) in this exact format:
[
  {{"id": 1, "question": "...", "difficulty": "Easy"}},
  {{"id": 2, "question": "...", "difficulty": "Easy"}},
  {{"id": 3, "question": "...", "difficulty": "Medium"}},
  {{"id": 4, "question": "...", "difficulty": "Medium"}},
  {{"id": 5, "question": "...", "difficulty": "Hard"}}
]"""

    # ── Call Gemini ────────────────────────────────────────────────────────
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Clean markdown fences if any
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.lower().startswith('json'):
                raw = raw[4:]

        import json
        questions = json.loads(raw)
        return jsonify({'questions': questions, 'cv_id': cv_id}), 200

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return jsonify({'error': f'AI question generation failed: {str(e)}'}), 500


# ════════════════════════════════════════════════════════════════════════════════
# ── Route: POST /api/interview/evaluate ──────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════════

@app.route('/api/interview/evaluate', methods=['POST'])
def evaluate_interview():
    """
    Questions + Answers নিয়ে Gemini দিয়ে evaluate করে।

    Request (JSON):
        { "field": "...", "questions": [...], "answers": [...] }

    Response:
        { "score": 78, "summary": "...", "strengths": [...],
          "improvements": [...], "questionFeedback": [...] }
    """
    import google.generativeai as genai
    import json

    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    field     = data.get('field', 'General')
    questions = data.get('questions', [])
    answers   = data.get('answers', [])

    if not questions or not answers:
        return jsonify({'error': 'Questions and answers are required.'}), 400

    # Build Q&A string for Gemini
    qa_pairs = ''
    for i, (q, a) in enumerate(zip(questions, answers)):
        qa_pairs += f"\nQ{i+1} [{q.get('difficulty','')}]: {q.get('question','')}\nAnswer: {a}\n"

    prompt = f"""You are an expert interviewer evaluating a candidate for: {field}.

Review the following Q&A and evaluate the candidate's performance:
{qa_pairs}

Return ONLY a JSON object (no markdown) with this exact format:
{{
  "score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": ["<area 1>", "<area 2>", "<area 3>"],
  "questionFeedback": [
    {{"question": "...", "feedback": "...", "score": <0-10>}},
    ...
  ]
}}"""

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        raw = response.text.strip()

        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.lower().startswith('json'):
                raw = raw[4:]

        result = json.loads(raw)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500


# ════════════════════════════════════════════════════════════════════════════════
# ── Route: GET /api/cv/profile ────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════════

@app.route('/api/cv/profile', methods=['GET'])
def get_cv_profile():
    """
    User এর current active CV এর সব parsed data return করে।
    Dashboard বা Profile page এ দেখানোর জন্য।
    """
    user_id = get_user_id_from_request()
    try:
        cv_data = db.get_cv_data(user_id)
        if not cv_data:
            return jsonify({'success': False, 'error': 'No CV found for this user.'}), 404
        return jsonify({'success': True, 'data': cv_data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# ── Route: GET /api/health ────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'InterviewAI backend is running!'}), 200


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    logger.info(f"🚀 Starting InterviewAI backend on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
