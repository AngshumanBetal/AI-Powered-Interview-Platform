/* ================================================================
   InterviewAI – Result Controller
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {
  // Protect page: redirect to login if not authenticated
  API.authGuard('../login/login.html');

  const resultDataRaw = sessionStorage.getItem('interviewResult');

  if (!resultDataRaw) {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) emptyState.style.display = 'block';
    return;
  }

  const result = JSON.parse(resultDataRaw);
  const resultContent = document.getElementById('result-content');
  if (resultContent) resultContent.style.display = 'block';

  // 1. Update Heading and Eyebrow with Field Info
  if (result.field) {
    const eyebrow = document.getElementById('result-eyebrow');
    const heading = document.getElementById('result-heading');
    if (eyebrow) eyebrow.textContent = result.field + ' Interview';
    if (heading) heading.textContent = result.field + ' Performance Review';
  }

  // 2. Animate Score Ring
  const scoreEl = document.getElementById('score-val');
  const targetScore = result.score || 0;
  let currentScore = 0;

  if (scoreEl) {
    if (targetScore > 0) {
      const interval = setInterval(() => {
        currentScore++;
        scoreEl.textContent = currentScore + '%';
        if (currentScore >= targetScore) {
          clearInterval(interval);
        }
      }, 15);
    } else {
      scoreEl.textContent = '0%';
    }
  }

  // 3. Populate Summary
  const summaryEl = document.getElementById('result-summary');
  if (summaryEl) {
    summaryEl.textContent = result.summary || 'No overall feedback summary provided.';
  }

  // 4. Populate Strengths
  const strengthsContainer = document.getElementById('strengths-container');
  if (strengthsContainer) {
    if (result.strengths && result.strengths.length > 0) {
      strengthsContainer.innerHTML = '';
      const ul = document.createElement('ul');
      ul.className = 'feedback-list strengths-list';
      result.strengths.forEach((strength) => {
        const li = document.createElement('li');
        li.textContent = strength;
        ul.appendChild(li);
      });
      strengthsContainer.appendChild(ul);
    } else {
      strengthsContainer.innerHTML = '<p>No strengths list generated.</p>';
    }
  }

  // 5. Populate Improvements
  const improvementsContainer = document.getElementById('improvements-container');
  if (improvementsContainer) {
    if (result.improvements && result.improvements.length > 0) {
      improvementsContainer.innerHTML = '';
      const ul = document.createElement('ul');
      ul.className = 'feedback-list improvements-list';
      result.improvements.forEach((imp) => {
        const li = document.createElement('li');
        li.textContent = imp;
        ul.appendChild(li);
      });
      improvementsContainer.appendChild(ul);
    } else {
      improvementsContainer.innerHTML = '<p>No improvement points generated.</p>';
    }
  }

  // 6. Populate Detailed QA Breakdown
  const qaBreakdown = document.getElementById('qa-breakdown');
  if (qaBreakdown) {
    if (result.questionFeedback && result.questionFeedback.length > 0 && result.questions) {
      qaBreakdown.innerHTML = '<h2 class="breakdown-title" style="margin-bottom: 24px;">Detailed Q&A Review</h2>';
      const grid = document.createElement('div');
      grid.className = 'qa-grid';

      result.questionFeedback.forEach((feedback, index) => {
        // Match question details
        const qObj = result.questions.find(q => q.id === feedback.id) || result.questions[index] || {};
        const qText = qObj.question || 'Interview Question';
        const qDiff = qObj.difficulty || 'medium';
        const answerText = result.answers[index] || '(No answer provided)';
        const score = feedback.score !== undefined ? feedback.score : 0;
        const evaluationText = feedback.feedback || 'No evaluation feedback provided for this question.';

        const card = document.createElement('div');
        card.className = 'qa-card glass-card';

        // Badge classes mapping
        let diffClass = 'badge--medium';
        if (qDiff.toLowerCase() === 'easy') diffClass = 'badge--easy';
        else if (qDiff.toLowerCase() === 'hard') diffClass = 'badge--hard';

        card.innerHTML = `
          <div class="qa-header">
            <h3 class="qa-title">Question ${index + 1}</h3>
            <div class="qa-badges">
              <span class="badge ${diffClass}">${qDiff}</span>
              <span class="badge badge--score">Score: ${score}/100</span>
            </div>
          </div>
          <p class="qa-question" style="font-size: 1.05rem; font-weight: 600; margin-bottom: 16px; color: var(--text);">${qText}</p>
          <div class="qa-box qa-box--answer">
            <span class="qa-box-label">Your Answer</span>
            <p>${escapeHTML(answerText)}</p>
          </div>
          <div class="qa-box qa-box--feedback">
            <span class="qa-box-label">AI Feedback</span>
            <p>${evaluationText}</p>
          </div>
        `;
        grid.appendChild(card);
      });
      qaBreakdown.appendChild(grid);
    }
  }

  // Helper to safely display user input
  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g,
      tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
      }[tag] || tag)
    );
  }
});
