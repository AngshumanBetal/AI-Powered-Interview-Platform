/* ================================================================
   InterviewAI – Landing Page Navigation Script
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const navActions = document.getElementById('nav-actions');

  if (!navActions) return;

  if (API.isLoggedIn()) {
    // User is logged in, show Dashboard and Logout button
    navActions.innerHTML = `
      <a class="btn btn-secondary" href="dashboard/dashboard.html">Dashboard</a>
      <button class="btn btn-primary" id="btn-logout">Logout</button>
    `;

    // Bind logout event
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        API.logout();
        window.location.reload();
      });
    }
  } else {
    // User is not logged in, show standard Login and Register buttons
    navActions.innerHTML = `
      <a class="btn btn-secondary" href="login/login.html">Login</a>
      <a class="btn btn-primary" href="register/register.html">Register</a>
    `;
  }
});
