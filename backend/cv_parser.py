"""
cv_parser.py
============
CV / Resume থেকে structured data বের করে।
Supported formats: PDF, DOCX, DOC, TXT

ব্যবহার:
    from cv_parser import CVParser
    parser = CVParser()
    data = parser.parse(file_path="resume.pdf")
"""

import re
import os
import json
import logging
from pathlib import Path

# Third-party (install via requirements.txt)
import pdfplumber          # pip install pdfplumber
import docx                # pip install python-docx

logger = logging.getLogger(__name__)


# ── Regex Patterns ─────────────────────────────────────────────────────────────

EMAIL_PATTERN    = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN    = re.compile(r'(\+?\d[\d\s\-\(\)]{7,}\d)')
LINKEDIN_PATTERN = re.compile(r'linkedin\.com/in/[\w\-]+', re.IGNORECASE)
GITHUB_PATTERN   = re.compile(r'github\.com/[\w\-]+', re.IGNORECASE)
URL_PATTERN      = re.compile(r'https?://[^\s]+', re.IGNORECASE)

# Section header keywords (case-insensitive)
SECTION_KEYWORDS = {
    'education'   : ['education', 'academic', 'qualification', 'degree'],
    'experience'  : ['experience', 'employment', 'work history', 'career', 'internship'],
    'skills'      : ['skills', 'technical skills', 'competencies', 'technologies', 'tools'],
    'projects'    : ['projects', 'personal projects', 'academic projects'],
    'certifications': ['certification', 'certificate', 'courses', 'training', 'award'],
    'languages'   : ['languages', 'language'],
    'summary'     : ['summary', 'objective', 'profile', 'about', 'introduction'],
    'achievements': ['achievements', 'accomplishments', 'honors'],
}

# Common programming / tech keywords for skill extraction
TECH_KEYWORDS = {
    'Python', 'Java', 'JavaScript', 'TypeScript', 'C', 'C++', 'C#', 'Go', 'Rust',
    'Ruby', 'Swift', 'Kotlin', 'PHP', 'R', 'MATLAB', 'Scala', 'Perl',
    'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'FastAPI',
    'Spring', 'Laravel', 'Rails', 'ASP.NET',
    'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Redis', 'Firebase', 'Oracle',
    'AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins',
    'Git', 'GitHub', 'GitLab', 'Linux', 'Windows', 'macOS',
    'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib',
    'HTML', 'CSS', 'Sass', 'Bootstrap', 'Tailwind',
    'REST', 'GraphQL', 'gRPC', 'WebSocket', 'OAuth', 'JWT',
    'Agile', 'Scrum', 'Kanban', 'CI/CD',
}


class CVParser:
    """Main CV parsing class — extracts all fields from a resume file."""

    def parse(self, file_path: str = None, file_bytes: bytes = None,
              filename: str = None) -> dict:
        """
        Parse a CV file and return extracted data as a dictionary.

        Parameters
        ----------
        file_path : str
            Path to the file on disk.
        file_bytes : bytes
            Raw bytes (use when coming from HTTP upload without saving).
        filename : str
            Original filename (needed with file_bytes to detect type).

        Returns
        -------
        dict with keys:
            raw_text, name, email, phone, linkedin, github, websites,
            summary, education, experience, skills, projects,
            certifications, languages, achievements
        """
        # ── 1. Extract raw text ────────────────────────────────────────────
        if file_path:
            filename = filename or os.path.basename(file_path)
            raw_text = self._extract_text(file_path=file_path, filename=filename)
        elif file_bytes and filename:
            # Write to temp file, parse, then delete
            import tempfile
            suffix = Path(filename).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            try:
                raw_text = self._extract_text(file_path=tmp_path, filename=filename)
            finally:
                os.unlink(tmp_path)
        else:
            raise ValueError("Provide either file_path or (file_bytes + filename).")

        if not raw_text or len(raw_text.strip()) < 20:
            logger.warning("CV text extraction yielded very little content.")
            return self._empty_result(raw_text or '')

        # ── 2. Split into lines for easier processing ──────────────────────
        lines = [l.strip() for l in raw_text.splitlines()]
        non_empty_lines = [l for l in lines if l]

        # ── 3. Extract structured fields ───────────────────────────────────
        sections  = self._split_into_sections(non_empty_lines)
        result = {
            'raw_text'       : raw_text,
            'name'           : self._extract_name(non_empty_lines),
            'email'          : self._extract_email(raw_text),
            'phone'          : self._extract_phone(raw_text),
            'linkedin'       : self._extract_linkedin(raw_text),
            'github'         : self._extract_github(raw_text),
            'websites'       : self._extract_websites(raw_text),
            'summary'        : self._get_section_text(sections, 'summary'),
            'education'      : self._parse_education(sections.get('education', [])),
            'experience'     : self._parse_experience(sections.get('experience', [])),
            'skills'         : self._parse_skills(sections.get('skills', []), raw_text),
            'projects'       : self._parse_projects(sections.get('projects', [])),
            'certifications' : self._get_section_text(sections, 'certifications'),
            'languages'      : self._get_section_text(sections, 'languages'),
            'achievements'   : self._get_section_text(sections, 'achievements'),
        }
        return result

    # ── Text Extraction ────────────────────────────────────────────────────────

    def _extract_text(self, file_path: str, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        try:
            if ext == '.pdf':
                return self._extract_pdf(file_path)
            elif ext in ('.docx',):
                return self._extract_docx(file_path)
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {e}")
            raise

    def _extract_pdf(self, path: str) -> str:
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return '\n'.join(text_parts)

    def _extract_docx(self, path: str) -> str:
        doc = docx.Document(path)
        return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())

    # ── Field Extractors ───────────────────────────────────────────────────────

    def _extract_name(self, lines: list) -> str:
        """First meaningful non-email, non-phone, non-URL line is likely the name."""
        for line in lines[:8]:  # Name is usually in first 8 lines
            if (len(line) > 2 and len(line) < 60
                    and not EMAIL_PATTERN.search(line)
                    and not PHONE_PATTERN.search(line)
                    and not re.search(r'http|www|linkedin|github', line, re.I)
                    and not any(kw in line.lower() for kw in ['resume', 'curriculum', 'cv', 'objective'])):
                # Heuristic: if it looks like a proper name (2+ words, mostly alphabets)
                words = line.split()
                if 1 <= len(words) <= 5 and all(re.match(r"[A-Za-z\.\'\-]+$", w) for w in words):
                    return line.strip()
        return ''

    def _extract_email(self, text: str) -> str:
        m = EMAIL_PATTERN.search(text)
        return m.group(0) if m else ''

    def _extract_phone(self, text: str) -> str:
        m = PHONE_PATTERN.search(text)
        if m:
            return re.sub(r'\s+', ' ', m.group(0)).strip()
        return ''

    def _extract_linkedin(self, text: str) -> str:
        m = LINKEDIN_PATTERN.search(text)
        return m.group(0) if m else ''

    def _extract_github(self, text: str) -> str:
        m = GITHUB_PATTERN.search(text)
        return m.group(0) if m else ''

    def _extract_websites(self, text: str) -> list:
        urls = URL_PATTERN.findall(text)
        # Exclude social media already captured above
        filtered = [u for u in urls if 'linkedin' not in u.lower() and 'github' not in u.lower()]
        # Remove duplicates preserving order
        seen = set()
        result = []
        for u in filtered:
            if u not in seen:
                seen.add(u)
                result.append(u)
        return result

    # ── Section Splitting ──────────────────────────────────────────────────────

    def _split_into_sections(self, lines: list) -> dict:
        """
        Split CV text into named sections by detecting section headers.
        Returns {section_name: [lines]} dict.
        """
        sections = {k: [] for k in SECTION_KEYWORDS}
        current_section = None

        for line in lines:
            lower = line.lower().strip(' :|-–—')
            detected = None
            for section, keywords in SECTION_KEYWORDS.items():
                if any(lower == kw or lower.startswith(kw) for kw in keywords):
                    detected = section
                    break

            if detected:
                current_section = detected
            elif current_section:
                sections[current_section].append(line)

        return sections

    def _get_section_text(self, sections: dict, key: str) -> str:
        lines = sections.get(key, [])
        return '\n'.join(lines).strip()

    # ── Structured Parsers ────────────────────────────────────────────────────

    def _parse_education(self, lines: list) -> list:
        """Extract education entries as list of dicts."""
        result = []
        current = {}
        degree_keywords = ['B.Tech', 'B.E', 'M.Tech', 'M.E', 'MBA', 'BCA', 'MCA',
                           'B.Sc', 'M.Sc', 'PhD', 'Bachelor', 'Master', 'Diploma',
                           'B.Com', 'M.Com', 'BA', 'MA', 'HSC', 'SSC', '10th', '12th']

        for line in lines:
            if any(kw.lower() in line.lower() for kw in degree_keywords):
                if current:
                    result.append(current)
                current = {'degree': line, 'institution': '', 'year': '', 'grade': ''}
            elif current:
                # Look for year
                year = re.search(r'\b(19|20)\d{2}\b', line)
                if year and not current['year']:
                    current['year'] = year.group(0)
                # Look for grade/percentage/CGPA
                grade = re.search(r'(\d+\.?\d*\s*(CGPA|GPA|%|percent))', line, re.I)
                if grade and not current['grade']:
                    current['grade'] = grade.group(0)
                # Remaining is institution
                elif not current['institution'] and len(line) > 3:
                    current['institution'] = line

        if current:
            result.append(current)
        return result

    def _parse_experience(self, lines: list) -> list:
        """Extract experience entries as list of dicts."""
        result = []
        current = {}
        date_pattern = re.compile(
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[\s\,\-]+\d{4}',
            re.IGNORECASE
        )

        for line in lines:
            # New entry if line contains a date range pattern
            if date_pattern.search(line) or re.search(r'\d{4}\s*[-–]\s*(\d{4}|present|current)', line, re.I):
                if current:
                    result.append(current)
                current = {
                    'title': '',
                    'company': '',
                    'duration': line,
                    'responsibilities': []
                }
            elif current:
                if not current['title']:
                    current['title'] = line
                elif not current['company']:
                    current['company'] = line
                elif line.startswith(('•', '-', '*', '·', '–')):
                    current['responsibilities'].append(line.lstrip('•-*·– '))
                else:
                    current['responsibilities'].append(line)

        if current:
            result.append(current)
        return result

    def _parse_skills(self, lines: list, raw_text: str) -> list:
        """Extract skills from the skills section + scan full text for tech keywords."""
        skills_set = set()

        # From skills section
        for line in lines:
            # Split by common delimiters
            parts = re.split(r'[,|•\-\n]', line)
            for p in parts:
                skill = p.strip()
                if 2 < len(skill) < 40:
                    skills_set.add(skill)

        # Also scan raw_text for known tech keywords
        for kw in TECH_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', raw_text, re.IGNORECASE):
                skills_set.add(kw)

        return sorted(skills_set, key=str.lower)

    def _parse_projects(self, lines: list) -> list:
        """Extract project entries as list of dicts."""
        result = []
        current = {}

        for line in lines:
            if line.isupper() or (len(line) < 80 and not line.startswith(('•', '-', '*'))):
                if current:
                    result.append(current)
                current = {'name': line, 'description': [], 'tech_used': []}
            elif current:
                # Detect tech stack mentions
                techs = [kw for kw in TECH_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', line, re.I)]
                current['tech_used'].extend(techs)
                current['description'].append(line.lstrip('•-* '))

        if current:
            result.append(current)
        return result

    def _empty_result(self, raw_text: str) -> dict:
        return {
            'raw_text': raw_text, 'name': '', 'email': '', 'phone': '',
            'linkedin': '', 'github': '', 'websites': [], 'summary': '',
            'education': [], 'experience': [], 'skills': [], 'projects': [],
            'certifications': '', 'languages': '', 'achievements': '',
        }
