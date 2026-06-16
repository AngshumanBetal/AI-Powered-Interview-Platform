/* ================================================================
   InterviewAI – Profile Controller
   ================================================================ */

document.addEventListener('DOMContentLoaded', async () => {
  // Protect page: redirect to login if not authenticated
  API.authGuard('../login/login.html');

  const form = document.getElementById('profile-form');
  const errorEl = document.getElementById('profile-error');
  const successEl = document.getElementById('profile-success');

  if (!form) return;

  const nameInput = document.getElementById('name');
  const emailInput = document.getElementById('email');
  const roleInput = document.getElementById('role');
  const skillsInput = document.getElementById('skills');
  const expInput = document.getElementById('experience');

  // 1. Fetch and populate user profile data
  try {
    const profile = await API.getProfile();
    if (profile) {
      nameInput.value = profile.name || '';
      emailInput.value = profile.email || '';
      roleInput.value = profile.role || '';
      skillsInput.value = profile.skills || '';
      expInput.value = profile.experience || '';
    }
  } catch (err) {
    showMsg(errorEl, err.message || 'Failed to load profile details.');
  }

  // 2. Handle form submission to update profile data
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Clear previous alerts
    errorEl.style.display = 'none';
    successEl.style.display = 'none';

    const profileData = {
      name: nameInput.value.trim(),
      role: roleInput.value.trim(),
      skills: skillsInput.value.trim(),
      experience: expInput.value
    };

    if (!profileData.name || !profileData.role || !profileData.skills || !profileData.experience) {
      showMsg(errorEl, 'Please fill in all required fields.');
      return;
    }

    try {
      const saveBtn = form.querySelector('button[type="submit"]');
      saveBtn.disabled = true;
      saveBtn.textContent = 'Saving...';

      await API.saveProfile(profileData);

      showMsg(successEl, 'Profile updated successfully!');
    } catch (err) {
      showMsg(errorEl, err.message || 'Failed to save profile details.');
    } finally {
      const saveBtn = form.querySelector('button[type="submit"]');
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save Profile';
      }
    }
  });

  // Helper to show warning/success alerts with automatic fadeout
  function showMsg(el, msg) {
    if (el) {
      el.textContent = msg;
      el.style.display = 'block';

      // Auto-hide after 5 seconds
      if (el === successEl) {
        setTimeout(() => {
          el.style.display = 'none';
        }, 5000);
      }
    }
  }
});
