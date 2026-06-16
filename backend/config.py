"""
config.py
=========
Project-wide configuration.
MySQL credentials এবং অন্য settings এখানে রাখো।
"""

import os

# ── MySQL Database ─────────────────────────────────────────────────────────────
# তোমার MySQL credentials এখানে দাও
DB_CONFIG = {
    'host'     : os.getenv('DB_HOST', 'localhost'),
    'port'     : int(os.getenv('DB_PORT', 3306)),
    'user'     : os.getenv('DB_USER', 'root'),         # ← তোমার MySQL username
    'password' : os.getenv('DB_PASSWORD', 'root'),     # ← তোমার MySQL password
    'database' : os.getenv('DB_NAME', 'interviewai'),  # ← database এর নাম
    'charset'  : 'utf8mb4',
    'use_unicode': True,
    'autocommit': False,
}

# ── File Upload Settings ───────────────────────────────────────────────────────
UPLOAD_FOLDER   = os.getenv('UPLOAD_FOLDER', 'uploads')  # CV files সাময়িক রাখার জায়গা
MAX_FILE_SIZE   = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}

# ── Gemini AI ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY  = os.getenv('GEMINI_API_KEY', '')   # ← তোমার Gemini API key

# ── Flask Server ───────────────────────────────────────────────────────────────
SECRET_KEY      = os.getenv('SECRET_KEY', 'change-this-in-production')
DEBUG           = os.getenv('DEBUG', 'True') == 'True'
PORT            = int(os.getenv('PORT', 5000))
HOST            = os.getenv('HOST', '0.0.0.0')
