/* ================================================================
   InterviewAI – Client API Utility & Local Database Mock
   ================================================================ */

const API_BASE_URL = 'http://localhost:5000/api';

// Helper to determine if we should call the backend or use local mock
async function request(method, path, body = null) {
  const url = `${API_BASE_URL}${path}`;
  const headers = { 'Content-Type': 'application/json' };

  // Attach token if logged in
  const token = localStorage.getItem('authToken');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers,
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.message || `API request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    // Check if it's a network connection issue (meaning backend is offline)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.warn(`[API] Connection to ${url} failed. Falling back to local mockup.`, error);
      throw { isNetworkError: true, message: error.message };
    }
    throw error;
  }
}

// ── Shared API & Mock API Interface ──────────────────────────────
const API = {
  // Check if user is logged in
  isLoggedIn() {
    return !!localStorage.getItem('currentUser') || !!localStorage.getItem('authToken');
  },

  // Get current logged in user details
  getCurrentUser() {
    const userJson = localStorage.getItem('currentUser');
    return userJson ? JSON.parse(userJson) : null;
  },

  // Logout the user
  logout() {
    localStorage.removeItem('currentUser');
    localStorage.removeItem('authToken');
    // Session-based result can also be cleared
    sessionStorage.removeItem('interviewResult');
  },

  // Authenticate user (Login)
  async login(email, password) {
    try {
      // Try backend first
      const data = await request('POST', '/auth/login', { email, password });

      // Save session info
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('currentUser', JSON.stringify(data.user));
      return data.user;
    } catch (error) {
      if (error.isNetworkError) {
        // Fallback: search user in local database
        const users = JSON.parse(localStorage.getItem('mockUsers') || '[]');
        const found = users.find(u => u.email === email && u.password === password);

        if (found) {
          const userObj = { name: found.name, email: found.email };
          localStorage.setItem('currentUser', JSON.stringify(userObj));
          return userObj;
        } else {
          throw new Error('Invalid email or password (Mock Database)');
        }
      }
      throw error;
    }
  },

  // Register a new user
  async register(name, email, password) {
    try {
      // Try backend first
      const data = await request('POST', '/auth/register', { name, email, password });
      return data;
    } catch (error) {
      if (error.isNetworkError) {
        // Fallback: save to local database
        const users = JSON.parse(localStorage.getItem('mockUsers') || '[]');
        const alreadyExists = users.some(u => u.email === email);

        if (alreadyExists) {
          throw new Error('Email is already registered (Mock Database)');
        }

        const newUser = { name, email, password };
        users.push(newUser);
        localStorage.setItem('mockUsers', JSON.stringify(users));

        // Create initial mock profile for user
        const profiles = JSON.parse(localStorage.getItem('mockProfiles') || '{}');
        profiles[email] = {
          name,
          email,
          role: '',
          skills: '',
          experience: ''
        };
        localStorage.setItem('mockProfiles', JSON.stringify(profiles));

        return { message: 'Registration successful (Mock Database)' };
      }
      throw error;
    }
  },

  // Get User Profile
  async getProfile() {
    const user = this.getCurrentUser();
    if (!user) throw new Error('User not authenticated');

    try {
      // Try backend first
      const data = await request('GET', `/profile?email=${encodeURIComponent(user.email)}`);
      return data;
    } catch (error) {
      if (error.isNetworkError) {
        // Fallback: load from local mock profiles
        const profiles = JSON.parse(localStorage.getItem('mockProfiles') || '{}');
        let profile = profiles[user.email];

        // If profile doesn't exist, initialize one
        if (!profile) {
          profile = {
            name: user.name || '',
            email: user.email,
            role: '',
            skills: '',
            experience: ''
          };
          profiles[user.email] = profile;
          localStorage.setItem('mockProfiles', JSON.stringify(profiles));
        }
        return profile;
      }
      throw error;
    }
  },

  // Save User Profile
  async saveProfile(profileData) {
    const user = this.getCurrentUser();
    if (!user) throw new Error('User not authenticated');

    try {
      // Try backend first
      const data = await request('POST', '/profile', profileData);

      // Update local cache of current user name if it changed
      if (profileData.name && profileData.name !== user.name) {
        user.name = profileData.name;
        localStorage.setItem('currentUser', JSON.stringify(user));
      }
      return data;
    } catch (error) {
      if (error.isNetworkError) {
        // Fallback: save to local mock profiles
        const profiles = JSON.parse(localStorage.getItem('mockProfiles') || '{}');
        profiles[user.email] = {
          ...profiles[user.email],
          ...profileData,
          email: user.email // ensure email is immutable
        };
        localStorage.setItem('mockProfiles', JSON.stringify(profiles));

        // Update local session cache
        if (profileData.name && profileData.name !== user.name) {
          user.name = profileData.name;
          localStorage.setItem('currentUser', JSON.stringify(user));
        }

        return { message: 'Profile saved successfully (Mock Database)' };
      }
      throw error;
    }
  },

  // Get Interview History
  async getHistory() {
    const user = this.getCurrentUser();
    if (!user) throw new Error('User not authenticated');

    try {
      // Try backend first
      const data = await request('GET', `/history?email=${encodeURIComponent(user.email)}`);
      return data;
    } catch (error) {
      if (error.isNetworkError) {
        // Fallback: get history from localStorage
        const allHistory = JSON.parse(localStorage.getItem('interviewHistory') || '[]');
        // Filter history by current user's email to avoid seeing other accounts' tests
        return allHistory.filter(item => item.userEmail === user.email);
      }
      throw error;
    }
  },

  // Save interview attempt to history
  async saveHistoryItem(item) {
    const user = this.getCurrentUser();
    if (!user) throw new Error('User not authenticated');

    const itemWithUser = {
      ...item,
      userEmail: user.email,
      date: new Date().toISOString()
    };

    try {
      // Try backend first
      const data = await request('POST', '/history', itemWithUser);
      return data;
    } catch (error) {
      if (error.isNetworkError) {
        // Fallback: add to localStorage list
        const history = JSON.parse(localStorage.getItem('interviewHistory') || '[]');
        history.push(itemWithUser);
        localStorage.setItem('interviewHistory', JSON.stringify(history));
        return { message: 'Result saved to history (Mock Database)' };
      }
      throw error;
    }
  },

  // Helper to force redirect to login if not logged in
  authGuard(redirectPath = '../login/login.html') {
    if (!this.isLoggedIn()) {
      window.location.href = redirectPath;
    }
  }
};
