-- ============================================================
-- InterviewAI — MySQL Database Setup Script
-- Run this once in MySQL Workbench or terminal:
--   mysql -u root -p < setup_db.sql
-- ============================================================

-- 1. Database তৈরি করো
CREATE DATABASE IF NOT EXISTS interviewai
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE interviewai;

-- ============================================================
-- Tables (db_manager.py এর init_tables() এই tables তৈরি করে)
-- এই file টা শুধু manually review বা restore করার জন্য।
-- ============================================================

-- 2. users
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150),
    email       VARCHAR(255) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    role        VARCHAR(100),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. cv_uploads — প্রতিটা upload এর record
CREATE TABLE IF NOT EXISTS cv_uploads (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    filename        VARCHAR(255),
    file_size_kb    FLOAT,
    uploaded_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active       TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. cv_basic_info — নাম, email, phone, linkedin ইত্যাদি
CREATE TABLE IF NOT EXISTS cv_basic_info (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    cv_id       INT NOT NULL UNIQUE,
    full_name   VARCHAR(200),
    email       VARCHAR(255),
    phone       VARCHAR(50),
    linkedin    VARCHAR(255),
    github      VARCHAR(255),
    websites    TEXT,
    summary     TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. cv_skills — প্রতিটা skill আলাদা row
CREATE TABLE IF NOT EXISTS cv_skills (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    cv_id       INT NOT NULL,
    skill_name  VARCHAR(150) NOT NULL,
    FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. cv_education
CREATE TABLE IF NOT EXISTS cv_education (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    cv_id       INT NOT NULL,
    degree      VARCHAR(255),
    institution VARCHAR(255),
    year        VARCHAR(20),
    grade       VARCHAR(50),
    FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. cv_experience
CREATE TABLE IF NOT EXISTS cv_experience (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    cv_id               INT NOT NULL,
    job_title           VARCHAR(255),
    company             VARCHAR(255),
    duration            VARCHAR(150),
    responsibilities    TEXT,
    FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. cv_projects
CREATE TABLE IF NOT EXISTS cv_projects (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    cv_id       INT NOT NULL,
    name        VARCHAR(255),
    description TEXT,
    tech_used   TEXT,
    FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. cv_extras — certifications, languages, achievements, raw_text
CREATE TABLE IF NOT EXISTS cv_extras (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    cv_id           INT NOT NULL UNIQUE,
    certifications  TEXT,
    languages       TEXT,
    achievements    TEXT,
    raw_text        LONGTEXT,
    FOREIGN KEY (cv_id) REFERENCES cv_uploads(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Test: একটা dummy user insert করো
-- ============================================================
INSERT IGNORE INTO users (name, email, password, role)
VALUES ('Test User', 'test@example.com', 'hashed_password_here', 'Software Engineer');

SELECT 'Database setup complete!' AS status;
