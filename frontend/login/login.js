/* ================================================================
   InterviewAI – Login Controller
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {
  // If user is already logged in, redirect to dashboard
  if (API.isLoggedIn()) {
    window.location.href = '../dashboard/dashboard.html';
    return;
  }

  const form = document.getElementById('login-form');
  const errorEl = document.getElementById('login-error');

  if (!form) return;

  // Check if redirected after successful registration
  const params = new URLSearchParams(window.location.search);
  if (params.get('registered') === 'true') {
    const successEl = document.createElement('div');
    successEl.className = 'success-msg';
    successEl.textContent = 'Account created successfully! Please log in below.';
    successEl.style.marginBottom = '20px';
    form.parentNode.insertBefore(successEl, form);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    if (!email || !password) {
      showError('Please fill in all fields.');
      return;
    }

    try {
      // Temporarily disable submit button to prevent double submits
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Logging in...';

      // Call authenticating method
      await API.login(email, password);

      // Redirect to Dashboard on success
      window.location.href = '../dashboard/dashboard.html';
    } catch (err) {
      showError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
      }
    }
  });

  function showError(msg) {
    if (errorEl) {
      errorEl.textContent = msg;
      errorEl.style.display = 'block';
    } else {
      alert(msg);
    }
  }
});
