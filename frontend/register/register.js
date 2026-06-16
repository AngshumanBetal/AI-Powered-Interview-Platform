/* ================================================================
   InterviewAI – Register Controller
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {
  // If user is already logged in, redirect to dashboard
  if (API.isLoggedIn()) {
    window.location.href = '../dashboard/dashboard.html';
    return;
  }

  const form = document.getElementById('register-form');
  const errorEl = document.getElementById('register-error');

  if (!form) return;

  // Handle Form Submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    if (!name || !email || !password) {
      showError('Please fill in all fields.');
      return;
    }

    if (password.length < 6) {
      showError('Password must be at least 6 characters.');
      return;
    }

    try {
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Creating account...';

      // Call registration API / mock storage
      await API.register(name, email, password);

      // Redirect to login page upon successful signup
      window.location.href = '../login/login.html?registered=true';
    } catch (err) {
      showError(err.message || 'Registration failed. Please try again.');
    } finally {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
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

// Password Strength Checker (Exposed globally for the HTML oninput attribute)
window.checkStrength = function (password) {
  const bar = document.getElementById('strength-bar');
  const label = document.getElementById('strength-label');
  const ruleLength = document.getElementById('rule-length');
  const ruleUpper = document.getElementById('rule-upper');
  const ruleNumber = document.getElementById('rule-number');
  const ruleSpecial = document.getElementById('rule-special');

  if (!bar || !label || !ruleLength || !ruleUpper || !ruleNumber || !ruleSpecial) return;

  let score = 0;
  const hasLength = password.length >= 6;
  const hasUpper = /[A-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

  ruleLength.textContent = (hasLength ? '✓' : '✕') + ' Minimum 6 characters';
  ruleLength.className = hasLength ? 'pass' : '';
  ruleUpper.textContent = (hasUpper ? '✓' : '✕') + ' One uppercase letter';
  ruleUpper.className = hasUpper ? 'pass' : '';
  ruleNumber.textContent = (hasNumber ? '✓' : '✕') + ' One number';
  ruleNumber.className = hasNumber ? 'pass' : '';
  ruleSpecial.textContent = (hasSpecial ? '✓' : '✕') + ' One special character (!@#$%)';
  ruleSpecial.className = hasSpecial ? 'pass' : '';

  if (hasLength) score++;
  if (hasUpper) score++;
  if (hasNumber) score++;
  if (hasSpecial) score++;

  if (password.length === 0) {
    bar.style.width = '0%';
    bar.className = 'strength-bar';
    label.textContent = 'Enter at least 6 characters';
    label.className = 'strength-label';
  } else if (score <= 1) {
    bar.style.width = '25%';
    bar.className = 'strength-bar weak';
    label.textContent = '🔴 Weak Password';
    label.className = 'strength-label weak';
  } else if (score === 2) {
    bar.style.width = '50%';
    bar.className = 'strength-bar fair';
    label.textContent = '🟠 Fair Password';
    label.className = 'strength-label fair';
  } else if (score === 3) {
    bar.style.width = '75%';
    bar.className = 'strength-bar good';
    label.textContent = '🟡 Good Password';
    label.className = 'strength-label good';
  } else {
    bar.style.width = '100%';
    bar.className = 'strength-bar strong';
    label.textContent = '🟢 Strong Password';
    label.className = 'strength-label strong';
  }
};
