# 🎯 InterviewAI - AI-Powered Interview Preparation Platform

[![GitHub license](https://img.shields.io/github/license/AngshumanBetal/AI-Powered-Interview-Platform?style=for-the-badge&color=blue)](LICENSE)
[![Frontend Status](https://img.shields.io/badge/Frontend-V1.0%20Complete-success?style=for-the-badge&logo=html5&logoColor=white)](frontend/)
[![Backend Status](https://img.shields.io/badge/Backend-Planned-orange?style=for-the-badge&logo=django&logoColor=white)](backend/)
[![Database Status](https://img.shields.io/badge/Database-MySQL-blue?style=for-the-badge&logo=mysql&logoColor=white)](backend/)

---

## 📖 Project Overview

**InterviewAI** is a comprehensive, production-ready mock interview platform designed to help students, developers, and job seekers ace real-world technical and behavioral interviews. By simulating real interview environments, the platform bridges the gap between passive learning and active interview readiness. 

Leveraging the power of the **Gemini API**, the application dynamically generates custom questions tailored to specific job roles (e.g., Frontend Developer, Backend Engineer, Data Scientist) and experience levels. It evaluates user responses in real-time, providing immediate scoring, detailed feedback on answer structure, and actionable insights to improve performance. The system follows a progressive learning path where users can track their historical attempts, analyze core strengths and weaknesses, and continuously build their confidence.

---

## ✨ Key Features

*   **Custom AI Question Generation**: Dynamically constructs interview questions based on selected roles, technical skills, and difficulty.
*   **Real-time AI Feedback & Scoring**: Analyzes submission content, grammar, and technical depth, delivering immediate performance metrics and constructive feedback.
*   **Performance Analytics Dashboard**: Tracks preparation milestones, average scores, and progress trends over time with visual analytics cards.
*   **Multi-Role Interview Simulation**: Offers tailored question flows for software engineering, web development, and custom career paths.
*   **Comprehensive Session History**: Logs all completed mock interviews with full question-and-answer transcripts for reference and self-review.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) | Creating a responsive, smooth, glassmorphic, and interactive user interface. |
| **Backend** | Python, Django, REST Framework | Powering high-performance API endpoints, authentication, and platform logic. |
| **Database** | MySQL | Storing relational tables for user credentials, interview sessions, and progress metrics. |
| **AI Engine** | Gemini API | Orchestrating real-time interview question generation and response evaluations. |
| **Development** | VS Code, Git, GitHub, Postman | Version control, collaborative repository hosting, and REST API endpoint testing. |

---

## 📂 Project Structure

```text
AI-Powered-Interview-Platform/
├── frontend/                # Client-side web application
│   ├── index.html           # Main landing page for the application
│   ├── style.css            # Custom layout and animations for landing page
│   ├── shared.css           # Global typography, color tokens, and utility classes
│   ├── script.js            # Frontend router and interactive transitions
│   ├── dashboard/           # User dashboard for tracking preparation progress
│   │   ├── dashboard.html   # Dashboard interface layout
│   │   └── dashboard.css    # Styles for statistics cards and dashboard grid
│   ├── interview/           # Live mock interview simulator environment
│   │   ├── interview.html   # Mock interview workspace with chat and webcam simulation
│   │   └── interview.css    # Layout and animation for active interview panel
│   ├── login/               # User authentication and login portal
│   │   ├── login.html       # Authentication form layout
│   │   └── login.css        # Styles for the login cards and glassmorphic inputs
│   ├── profile/             # User profile settings and preferences page
│   │   ├── profile.html     # User profile and details update page
│   │   └── profile.css      # Styling for profile inputs and image upload UI
│   ├── register/            # Account creation and registration form
│   │   ├── register.html    # Signup and onboarding form layout
│   │   └── register.css     # Styling for registration cards and validations
│   └── result/              # Interactive AI feedback and score breakdown portal
│       ├── result.html      # Scorecard and feedback presentation dashboard
│       └── result.css       # Visual progress bars and breakdown style definitions
├── backend/                 # API service components (To be initialized)
├── docs/                    # Development documentation and system design assets
├── LICENSE                  # MIT License details
└── README.md                # Project documentation and roadmap log
```

---

## 📈 Development Progress Log

### Day 1
* Initialized project workspace, repository, and created the core landing files: [index.html](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/index.html), [style.css](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/style.css), [shared.css](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/shared.css), and [script.js](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/script.js).
* Configured basic project setup including repository subfolders, license, and global gitignore.

### Day 2
* Created the login interface components: [login.html](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/login/login.html) and [login.css](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/login/login.css).
* Designed user login form structure, input labels, login button, and landing redirects.

### Day 3
* Designed registration form components: [register.html](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/register/register.html) and [register.css](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/register/register.css).
* Configured validation UI, hover transitions, and redirection paths back to login page.

### Day 4
* Developed student dashboard components: [dashboard.html](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/dashboard/dashboard.html) and [dashboard.css](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/dashboard/dashboard.css).
* Built progress tracking widgets, statistics grid layout, and navigation redirection items.

### Day 5
* Designed mock simulation and results screens: [interview.html](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/interview/interview.html), [interview.css](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/interview/interview.css), [result.html](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/result/result.html), and [result.css](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/result/result.css).
* Created user profile view and configuration components: [profile.html](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/profile/profile.html) and [profile.css](file:///d:/Desktop/AI-Powered-Interview-Platform/AI-Powered-Interview-Platform/frontend/profile/profile.css).

### Day 6
* Created all client-side JavaScript logic files: [login.js](frontend/login/login.js), [register.js](frontend/register/register.js), [dashboard.js](frontend/dashboard/dashboard.js), [profile.js](frontend/profile/profile.js), and [result.js](frontend/result/result.js).
* Implemented form validation, password strength meter, and auth-guard redirects across all pages.
* Added password show/hide toggle, animated score counters, and dynamic history rendering on the dashboard.
* Updated [api.js](frontend/api.js) with `startInterview()` and `evaluateInterview()` methods, including full mock fallback (platform works without backend).
* Updated [interview.js](frontend/interview/interview.js) to use the unified API utility for question fetching and evaluation.
* Enhanced [script.js](frontend/script.js) with scroll-triggered animations, smooth anchor scrolling, and navbar shadow on scroll.

### Day 7
* Created [auth.py](backend/auth.py) — Flask Blueprint for User Authentication: Register, Login, Logout, and Profile endpoints with JWT token support.
* Updated [db_manager.py](backend/db_manager.py) — added `create_user()`, `get_user_by_email()`, `save_interview_result()`, and `get_interview_history()` methods; added `interview_sessions` table.
* Updated [app.py](backend/app.py) — registered Auth Blueprint, added `/api/profile` and `/api/history` routes with real JWT validation.
* Updated [setup_db.sql](backend/setup_db.sql) — added `interview_sessions` and `interview_answers` tables.
* Updated [requirements.txt](backend/requirements.txt) — added `PyJWT` and `bcrypt` dependencies.

---

## 🎯 Current Status & Next Steps

*   **Current Milestone**: Full Frontend JavaScript Wiring + Backend Auth API completed (Day 6 & 7).
*   **Next Milestone**: Django REST Framework migration and full Gemini API end-to-end integration.
*   **Deployment Milestone**: Connecting backend to production MySQL and hosting the full platform.

---

## 📅 Roadmap

- [x] Version 1 Frontend static design and page layouts *(Day 1–5)*
- [x] Client-side interactivity and validation — Vanilla JS *(Day 6)*
- [x] Flask REST backend — CV parsing + AI question generation *(Day 5 bonus)*
- [x] User Authentication API — Register / Login / JWT *(Day 7)*
- [ ] Django REST Framework migration
- [ ] Gemini API full integration (end-to-end interview flow)
- [ ] Session tracking and history dashboard with real database
- [ ] PDF report export functionality
- [ ] Deploying client-side and server-side components to production

---

## 👨‍💻 Developer & Learning Philosophy

**Babai** (BCA Student)

> 🚀 **Learning Web Development**: Learn With Practical. Build first. Learn along the way.

---

## ⭐ Future Goals

Our long-term target is to transition InterviewAI from a practice repository into a production-grade SaaS tool. We aim to support audio-to-text response submission, multiple concurrent languages, resume-based tailoring, and coding environment mock panels to prepare applicants for top-tier software developer interviews.
