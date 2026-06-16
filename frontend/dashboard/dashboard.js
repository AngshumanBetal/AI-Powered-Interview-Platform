/* ================================================================
   InterviewAI – Dashboard Controller
   ================================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  // Protect page: redirect to login if not authenticated
  API.authGuard('../login/login.html');

  const statsValues = document.querySelectorAll('.stat-value');
  const historyList = document.getElementById('history-list');

  // Load and display stats & history list
  try {
    const history = await API.getHistory();

    // 1. Calculate and update stat badges
    const completedCount = history.length;
    let averageScore = 0;

    if (completedCount > 0) {
      const totalScore = history.reduce((sum, item) => sum + (item.score || 0), 0);
      averageScore = Math.round(totalScore / completedCount);
    }

    if (statsValues.length >= 3) {
      statsValues[0].textContent = completedCount;
      statsValues[1].textContent = `${averageScore}%`;
      statsValues[2].textContent = '0'; // Pending reviews (always 0 once evaluated)
    }

    // 2. Render history list items
    if (!historyList) return;

    if (completedCount === 0) {
      historyList.innerHTML = `
        <p class="no-history">No interview attempts yet. Click "Start Interview" to begin practicing!</p>
      `;
      return;
    }

    // Sort history by date descending
    const sortedHistory = [...history].sort((a, b) => new Date(b.date) - new Date(a.date));

    historyList.innerHTML = '';
    sortedHistory.forEach((item, index) => {
      const dateStr = new Date(item.date).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });

      // Map score text colors
      let scoreClass = 'fail';
      if (item.score >= 75) scoreClass = 'pass';
      else if (item.score >= 50) scoreClass = 'warn';

      const historyItem = document.createElement('div');
      historyItem.className = 'history-item';
      historyItem.innerHTML = `
        <div class="history-details">
          <span class="history-field">${escapeHTML(item.field || 'Interview Session')}</span>
          <span class="history-date">${dateStr}</span>
        </div>
        <div class="history-score-wrapper">
          <span class="history-score ${scoreClass}">${item.score || 0}%</span>
          <button class="btn btn-secondary btn-view-feedback" style="min-height: 36px; padding: 6px 14px; font-size: 0.82rem;">
            View Feedback
          </button>
        </div>
      `;

      // Click event to restore result and go to result page
      const viewBtn = historyItem.querySelector('.btn-view-feedback');
      viewBtn.addEventListener('click', () => {
        // Store full result object in sessionStorage for result.html to pick up
        sessionStorage.setItem('interviewResult', JSON.stringify({
          field: item.field,
          score: item.score,
          summary: item.summary,
          strengths: item.strengths,
          improvements: item.improvements,
          questionFeedback: item.questionFeedback,
          questions: item.questions,
          answers: item.answers
        }));
        window.location.href = '../result/result.html';
      });

      historyList.appendChild(historyItem);
    });

  } catch (err) {
    console.error('Failed to load dashboard data:', err);
    if (historyList) {
      historyList.innerHTML = `
        <p class="no-history" style="color: var(--danger);">Failed to load history: ${err.message}</p>
      `;
    }
  }

  // Helper to escape HTML characters
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
