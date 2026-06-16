"""
db_manager.py
=============
MySQL connection manager + CV data save করার সব functions।

ব্যবহার:
    from db_manager import DBManager
    db = DBManager()
    db.init_tables()                  # একবার run করলেই হবে
    cv_id = db.save_cv_data(user_id=1, cv_data=parsed_dict, filename="resume.pdf")
"""

import json
import logging
from datetime import datetime
from typing import Optional

import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG

logger = logging.getLogger(__name__)


class DBManager:
    """MySQL database manager for the InterviewAI platform."""

    def __init__(self):
        self.connection = None
        self._connect()

    # ── Connection ────────────────────────────────────────────────────────────

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                logger.info("✅ MySQL connected successfully.")
        except Error as e:
            logger.error(f"❌ MySQL connection failed: {e}")
            raise

    def _ensure_connected(self):
        """Reconnect if the connection was dropped."""
        if not self.connection or not self.connection.is_connected():
            logger.warning("MySQL connection lost — reconnecting...")
            self._connect()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed.")

    # ── Table Initialization ──────────────────────────────────────────────────

    def init_tables(self):
        """
        Create all required tables if they don't exist.
        Call this once at application startup.
        """
        self._ensure_connected()
        cursor = self.connection.cursor()

        tables = [
            # ── users ──────────────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS users (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                name        VARCHAR(150),
                email       VARCHAR(255) UNIQUE NOT NULL,
                password    VARCHAR(255) NOT NULL,
                role        VARCHAR(100),
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,

            # ── cv_uploads ─────────────────────────────────────────────────
            # একটি user অনেকবার CV upload করতে পারে।
            # is_active=1 মানে সেটাই currently active CV।
            """
            CREATE TABLE IF NOT EXISTS cv_uploads (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                user_id         INT NOT NULL,
                filename        VARCHAR(255),
                file_size_kb    FLOAT,
                uploaded_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active       TINYINT(1) DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,

            # ── cv_basic_info ──────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS cv_basic_info (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                cv_id       INT NOT NULL UNIQUE,
                full_name   VARCHAR(200),
                email       VARCHAR(255),
                phone       VARCHAR(50),
                linkedin    VARCHAR(255),
                github      VARCHAR(255),
                websites    TEXT,               -- JSON array
                summary     TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,

            # ── cv_skills ──────────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS cv_skills (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                cv_id       INT NOT NULL,
                skill_name  VARCHAR(150) NOT NULL,
                FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,

            # ── cv_education ───────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS cv_education (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                cv_id       INT NOT NULL,
                degree      VARCHAR(255),
                institution VARCHAR(255),
                year        VARCHAR(20),
                grade       VARCHAR(50),
                FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,

            # ── cv_experience ──────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS cv_experience (
                id                  INT AUTO_INCREMENT PRIMARY KEY,
                cv_id               INT NOT NULL,
                job_title           VARCHAR(255),
                company             VARCHAR(255),
                duration            VARCHAR(150),
                responsibilities    TEXT,       -- JSON array of strings
                FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,

            # ── cv_projects ────────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS cv_projects (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                cv_id       INT NOT NULL,
                name        VARCHAR(255),
                description TEXT,               -- JSON array of description lines
                tech_used   TEXT,               -- JSON array of techs
                FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,

            # ── cv_extras ──────────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS cv_extras (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                cv_id           INT NOT NULL UNIQUE,
                certifications  TEXT,
                languages       TEXT,
                achievements    TEXT,
                raw_text        LONGTEXT,
                FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        ]

        try:
            for sql in tables:
                cursor.execute(sql)
            self.connection.commit()
            logger.info("✅ All tables initialized.")
        except Error as e:
            logger.error(f"Table init failed: {e}")
            raise
        finally:
            cursor.close()

    # ── Save CV Data ──────────────────────────────────────────────────────────

    def save_cv_data(self, user_id: int, cv_data: dict,
                     filename: str = 'resume', file_size_kb: float = 0.0) -> int:
        """
        CV parser থেকে পাওয়া dict টা নিয়ে সব টেবিলে save করে।

        Returns
        -------
        cv_id : int
            cv_uploads table এ নতুন row এর ID।
        """
        self._ensure_connected()

        # আগের active CV গুলো deactivate করো
        self._deactivate_previous_cvs(user_id)

        # ── 1. cv_uploads ──────────────────────────────────────────────────
        cv_id = self._insert_cv_upload(user_id, filename, file_size_kb)

        # ── 2. cv_basic_info ───────────────────────────────────────────────
        self._insert_basic_info(cv_id, cv_data)

        # ── 3. cv_skills ───────────────────────────────────────────────────
        self._insert_skills(cv_id, cv_data.get('skills', []))

        # ── 4. cv_education ────────────────────────────────────────────────
        self._insert_education(cv_id, cv_data.get('education', []))

        # ── 5. cv_experience ───────────────────────────────────────────────
        self._insert_experience(cv_id, cv_data.get('experience', []))

        # ── 6. cv_projects ─────────────────────────────────────────────────
        self._insert_projects(cv_id, cv_data.get('projects', []))

        # ── 7. cv_extras ───────────────────────────────────────────────────
        self._insert_extras(cv_id, cv_data)

        logger.info(f"✅ CV data saved. cv_id={cv_id}, user_id={user_id}")
        return cv_id

    # ── Private Insert Helpers ────────────────────────────────────────────────

    def _deactivate_previous_cvs(self, user_id: int):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE cv_uploads SET is_active = 0 WHERE user_id = %s AND is_active = 1",
                (user_id,)
            )
            self.connection.commit()
        finally:
            cursor.close()

    def _insert_cv_upload(self, user_id: int, filename: str, file_size_kb: float) -> int:
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """INSERT INTO cv_uploads (user_id, filename, file_size_kb)
                   VALUES (%s, %s, %s)""",
                (user_id, filename, round(file_size_kb, 2))
            )
            self.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    def _insert_basic_info(self, cv_id: int, data: dict):
        cursor = self.connection.cursor()
        try:
            websites_json = json.dumps(data.get('websites', []))
            cursor.execute(
                """INSERT INTO cv_basic_info
                   (cv_id, full_name, email, phone, linkedin, github, websites, summary)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    cv_id,
                    data.get('name', '')[:200],
                    data.get('email', '')[:255],
                    data.get('phone', '')[:50],
                    data.get('linkedin', '')[:255],
                    data.get('github', '')[:255],
                    websites_json,
                    data.get('summary', ''),
                )
            )
            self.connection.commit()
        finally:
            cursor.close()

    def _insert_skills(self, cv_id: int, skills: list):
        if not skills:
            return
        cursor = self.connection.cursor()
        try:
            rows = [(cv_id, str(s)[:150]) for s in skills if s]
            cursor.executemany(
                "INSERT INTO cv_skills (cv_id, skill_name) VALUES (%s, %s)",
                rows
            )
            self.connection.commit()
        finally:
            cursor.close()

    def _insert_education(self, cv_id: int, education: list):
        if not education:
            return
        cursor = self.connection.cursor()
        try:
            for edu in education:
                cursor.execute(
                    """INSERT INTO cv_education (cv_id, degree, institution, year, grade)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (
                        cv_id,
                        str(edu.get('degree', ''))[:255],
                        str(edu.get('institution', ''))[:255],
                        str(edu.get('year', ''))[:20],
                        str(edu.get('grade', ''))[:50],
                    )
                )
            self.connection.commit()
        finally:
            cursor.close()

    def _insert_experience(self, cv_id: int, experience: list):
        if not experience:
            return
        cursor = self.connection.cursor()
        try:
            for exp in experience:
                responsibilities_json = json.dumps(exp.get('responsibilities', []))
                cursor.execute(
                    """INSERT INTO cv_experience
                       (cv_id, job_title, company, duration, responsibilities)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (
                        cv_id,
                        str(exp.get('title', ''))[:255],
                        str(exp.get('company', ''))[:255],
                        str(exp.get('duration', ''))[:150],
                        responsibilities_json,
                    )
                )
            self.connection.commit()
        finally:
            cursor.close()

    def _insert_projects(self, cv_id: int, projects: list):
        if not projects:
            return
        cursor = self.connection.cursor()
        try:
            for proj in projects:
                description_json = json.dumps(proj.get('description', []))
                tech_json = json.dumps(proj.get('tech_used', []))
                cursor.execute(
                    """INSERT INTO cv_projects (cv_id, name, description, tech_used)
                       VALUES (%s, %s, %s, %s)""",
                    (
                        cv_id,
                        str(proj.get('name', ''))[:255],
                        description_json,
                        tech_json,
                    )
                )
            self.connection.commit()
        finally:
            cursor.close()

    def _insert_extras(self, cv_id: int, data: dict):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """INSERT INTO cv_extras (cv_id, certifications, languages, achievements, raw_text)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    cv_id,
                    data.get('certifications', ''),
                    data.get('languages', ''),
                    data.get('achievements', ''),
                    data.get('raw_text', ''),
                )
            )
            self.connection.commit()
        finally:
            cursor.close()

    # ── Read Helpers ──────────────────────────────────────────────────────────

    def get_cv_data(self, user_id: int) -> Optional[dict]:
        """
        user_id দিলে তার সবচেয়ে recent active CV এর সব data return করে।
        Returns None if no CV found.
        """
        self._ensure_connected()
        cursor = self.connection.cursor(dictionary=True)
        try:
            # Get latest active cv_id
            cursor.execute(
                """SELECT id, filename, uploaded_at FROM cv_uploads
                   WHERE user_id = %s AND is_active = 1
                   ORDER BY uploaded_at DESC LIMIT 1""",
                (user_id,)
            )
            upload = cursor.fetchone()
            if not upload:
                return None
            cv_id = upload['id']

            # Fetch all related data
            cursor.execute("SELECT * FROM cv_basic_info WHERE cv_id = %s", (cv_id,))
            basic = cursor.fetchone() or {}

            cursor.execute("SELECT skill_name FROM cv_skills WHERE cv_id = %s", (cv_id,))
            skills = [r['skill_name'] for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM cv_education WHERE cv_id = %s", (cv_id,))
            education = cursor.fetchall()

            cursor.execute("SELECT * FROM cv_experience WHERE cv_id = %s", (cv_id,))
            experience_rows = cursor.fetchall()
            experience = []
            for row in experience_rows:
                row['responsibilities'] = json.loads(row.get('responsibilities') or '[]')
                experience.append(row)

            cursor.execute("SELECT * FROM cv_projects WHERE cv_id = %s", (cv_id,))
            project_rows = cursor.fetchall()
            projects = []
            for row in project_rows:
                row['description'] = json.loads(row.get('description') or '[]')
                row['tech_used'] = json.loads(row.get('tech_used') or '[]')
                projects.append(row)

            cursor.execute("SELECT * FROM cv_extras WHERE cv_id = %s", (cv_id,))
            extras = cursor.fetchone() or {}

            return {
                'cv_id'          : cv_id,
                'filename'       : upload['filename'],
                'uploaded_at'    : str(upload['uploaded_at']),
                'name'           : basic.get('full_name', ''),
                'email'          : basic.get('email', ''),
                'phone'          : basic.get('phone', ''),
                'linkedin'       : basic.get('linkedin', ''),
                'github'         : basic.get('github', ''),
                'websites'       : json.loads(basic.get('websites') or '[]'),
                'summary'        : basic.get('summary', ''),
                'skills'         : skills,
                'education'      : education,
                'experience'     : experience,
                'projects'       : projects,
                'certifications' : extras.get('certifications', ''),
                'languages'      : extras.get('languages', ''),
                'achievements'   : extras.get('achievements', ''),
            }
        finally:
            cursor.close()

    def get_all_cv_uploads(self, user_id: int) -> list:
        """সব CV upload history দেখানোর জন্য।"""
        self._ensure_connected()
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT id, filename, file_size_kb, uploaded_at, is_active
                   FROM cv_uploads WHERE user_id = %s ORDER BY uploaded_at DESC""",
                (user_id,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
