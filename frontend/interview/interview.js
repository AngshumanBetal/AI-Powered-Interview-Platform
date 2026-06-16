/* ================================================================
   InterviewAI — Interview Engine (Backend-Powered)
   API key is stored on the server. Frontend only uploads CV.
   ================================================================ */

const BACKEND_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
  // Protect page: redirect to login if not authenticated
  API.authGuard('../login/login.html');

  // ── State ──────────────────────────────────────────────────────
  let questions = [];
  let answers = [];
  let currentQ = 0;
  let selectedField = 'Data Science';
  let cvFile = null; // Store actual File object for FormData upload

  // ── DOM refs ───────────────────────────────────────────────────
  const $setup = document.getElementById('step-setup');
  const $loading = document.getElementById('loading-panel');
  const $interview = document.getElementById('interview-panel');
  const $evaluating = document.getElementById('evaluating-panel');
  const $setupError = document.getElementById('setup-error');
  const $intError = document.getElementById('interview-error');
  const $qTitle = document.getElementById('question-title');
  const $qText = document.getElementById('question-text');
  const $qCounter = document.getElementById('question-counter');
  const $fieldBadge = document.getElementById('selected-field-badge');
  const $answer = document.getElementById('answer');
  const $btnStart = document.getElementById('btn-start-interview');
  const $btnSubmit = document.getElementById('btn-submit-answer');
  const $btnSkip = document.getElementById('btn-skip');
  const $cvFileInput = document.getElementById('cv-file');
  const $cvDropzone = document.getElementById('cv-dropzone');
  const $cvFileInfo = document.getElementById('cv-file-info');
  const $cvFileName = document.getElementById('cv-file-name');
  const $cvRemove = document.getElementById('cv-remove');

  // ── Field selection ────────────────────────────────────────────
  document.querySelectorAll('input[name="field"]').forEach((r) => {
    r.addEventListener('change', function () {
      selectedField = this.value;
      if ($fieldBadge) $fieldBadge.textContent = this.value;
    });
  });

  // ── CV Upload (Drag & Drop) ────────────────────────────────────
  if ($cvDropzone) {
    $cvDropzone.addEventListener('click', () => { if ($cvFileInput) $cvFileInput.click(); });

    $cvDropzone.addEventListener('dragover', function (e) {
      e.preventDefault();
      this.classList.add('dragover');
    });
    $cvDropzone.addEventListener('dragleave', function () {
      this.classList.remove('dragover');
    });
    $cvDropzone.addEventListener('drop', function (e) {
      e.preventDefault();
      this.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        handleCVFile(e.dataTransfer.files[0]);
      }
    });
  }

  if ($cvFileInput) {
    $cvFileInput.addEventListener('change', function () {
      if (this.files.length) handleCVFile(this.files[0]);
    });
  }

  if ($cvRemove) {
    $cvRemove.addEventListener('click', () => {
      cvFile = null;
      if ($cvFileInput) $cvFileInput.value = '';
      if ($cvFileInfo) $cvFileInfo.style.display = 'none';
      if ($cvDropzone) $cvDropzone.style.display = '';
    });
  }

  function handleCVFile(file) {
    const allowedTypes = ['application/pdf', 'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'];

    if (file.size > 5 * 1024 * 1024) {
      showError($setupError, 'File size must be under 5MB.');
      return;
    }

    cvFile = file; // Store for FormData upload
    if ($cvFileName) $cvFileName.textContent = file.name + ' (' + (file.size / 1024).toFixed(1) + ' KB)';
    if ($cvFileInfo) $cvFileInfo.style.display = '';
    if ($cvDropzone) $cvDropzone.style.display = 'none';
  }

  // ── Show/Hide helpers ──────────────────────────────────────────
  function showSection(el) { if (el) el.style.display = ''; }
  function hideSection(el) { if (el) el.style.display = 'none'; }

  function showError(el, msg) {
    if (!el) return;
    el.textContent = msg;
    el.style.display = '';
    setTimeout(() => { el.style.display = 'none'; }, 7000);
  }

  // ── Backend API helper ─────────────────────────────────────────
  async function callBackend(endpoint, method = 'POST', body = null, isFormData = false) {
    const headers = {};
    const token = localStorage.getItem('authToken');
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = { method, headers };

    if (body) {
      if (isFormData) {
        // Don't set Content-Type for FormData — browser sets it with boundary
        options.body = body;
      } else {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
      }
    }

    const res = await fetch(`${BACKEND_URL}${endpoint}`, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || `Request failed (${res.status})`);
    }
    return await res.json();
  }

  // ── Start Interview: Upload CV → Backend generates questions ───
  if ($btnStart) {
    $btnStart.addEventListener('click', async () => {
      if (!cvFile) {
        showError($setupError, 'Please upload your CV before starting the interview.');
        return;
      }

      hideSection($setup);
      showSection($loading);

      try {
        // Send CV + selected field to backend via FormData
        const formData = new FormData();
        formData.append('cv', cvFile);
        formData.append('field', selectedField);

        // Backend reads CV, calls Gemini, returns questions array
        const data = await callBackend('/interview/start', 'POST', formData, true);

        // Expected response: { questions: [{id, question, difficulty}, ...] }
        questions = data.questions;
        if (!Array.isArray(questions) || questions.length === 0) {
          throw new Error('No questions received from server. Please try again.');
        }

        answers = new Array(questions.length).fill('');
        currentQ = 0;

        hideSection($loading);
        showSection($interview);
        renderQuestion();
      } catch (err) {
        hideSection($loading);
        showSection($setup);
        showError($setupError, 'Error: ' + err.message);
      }
    });
  }

  // ── Render current question ────────────────────────────────────
  function renderQuestion() {
    const q = questions[currentQ];
    if ($qCounter) $qCounter.textContent = `Question ${currentQ + 1} of ${questions.length}`;
    if ($qTitle) $qTitle.textContent = `Question ${currentQ + 1}`;

    // Dynamic difficulty badge color
    let diffColor = '#fdcb6e'; // yellow = medium
    if (q.difficulty.toLowerCase() === 'easy') diffColor = '#00d2a0';
    else if (q.difficulty.toLowerCase() === 'hard') diffColor = '#ff6b6b';

    if ($qText) {
      $qText.innerHTML = `
        <span class="eyebrow" style="background:rgba(255,255,255,0.04); border-color:${diffColor}; color:${diffColor}; margin-bottom:16px;">
          ${q.difficulty}
        </span>
        <p style="font-size:1.15rem; line-height:1.6; margin-top:10px;">${q.question}</p>
      `;
    }

    if ($answer) {
      $answer.value = answers[currentQ] || '';
      $answer.focus();
    }

    // Update button text for last question
    if (currentQ === questions.length - 1) {
      $btnSubmit.innerHTML = 'Finish Interview <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>';
      if ($btnSkip) $btnSkip.style.display = 'none';
    } else {
      $btnSubmit.innerHTML = 'Next Question <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>';
      if ($btnSkip) $btnSkip.style.display = '';
    }
  }

  // ── Submit / Next ──────────────────────────────────────────────
  if ($btnSubmit) {
    $btnSubmit.addEventListener('click', async () => {
      const ans = $answer.value.trim();
      if (!ans) {
        showError($intError, 'Please type your answer before submitting.');
        return;
      }
      answers[currentQ] = ans;

      if (currentQ < questions.length - 1) {
        currentQ++;
        renderQuestion();
      } else {
        await evaluateInterview();
      }
    });
  }

  if ($btnSkip) {
    $btnSkip.addEventListener('click', async () => {
      answers[currentQ] = '(Skipped)';
      if (currentQ < questions.length - 1) {
        currentQ++;
        renderQuestion();
      } else {
        await evaluateInterview();
      }
    });
  }

  // ── Evaluate: Send Q&A pairs to backend for Gemini evaluation ─
  async function evaluateInterview() {
    hideSection($interview);
    showSection($evaluating);

    try {
      // Send questions + answers to backend
      // Backend calls Gemini with the evaluation prompt and returns result
      const data = await callBackend('/interview/evaluate', 'POST', {
        field: selectedField,
        questions: questions,
        answers: answers
      });

      // Expected response: { score, summary, strengths, improvements, questionFeedback }
      const resultDetails = {
        field: selectedField,
        score: data.score || 0,
        summary: data.summary || 'Evaluation completed.',
        strengths: data.strengths || [],
        improvements: data.improvements || [],
        questionFeedback: data.questionFeedback || [],
        questions: questions,
        answers: answers
      };

      // Save to history using the API utility
      try {
        await API.saveHistoryItem(resultDetails);
      } catch (e) {
        console.error('Failed to save history:', e);
      }

      // Store current result in sessionStorage and navigate to result page
      sessionStorage.setItem('interviewResult', JSON.stringify(resultDetails));
      window.location.href = '../result/result.html';

    } catch (err) {
      hideSection($evaluating);
      showSection($interview);
      showError($intError, 'Evaluation error: ' + err.message);
    }
  }
});
