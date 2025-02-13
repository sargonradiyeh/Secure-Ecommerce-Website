// axiosConfig.js
import axios from 'axios';
import config from './config';

const instance = axios.create({
  baseURL: config.server,
  withCredentials: true
});

const logout = async () => {
  try {
    await instance.post('/api/logout'); // Call the logout API endpoint
  } catch (error) {
    console.error('Logout failed');
  } finally {
    localStorage.removeItem('token'); // Remove the token from localStorage
    delete instance.defaults.headers.common['Authorization']; // Remove the Authorization header
    window.location.href = '/login'; // Redirect to the login page
  }
};

function getAuthToken() {
  return localStorage.getItem('token');
}

function getCsrfTokenFromCookie() {
  const name = 'csrf_token=';
  const cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    if (cookie.startsWith(name)) {
      return cookie.substring(name.length);
    }
  }
  return '';
}

// Request interceptor
instance.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // CSRF token code remains the same
    const csrfToken = getCsrfTokenFromCookie();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }

    return config;
  },
  (error) => Promise.reject(error)
);
// Response interceptor
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    const currentPath = window.location.pathname;
    if (error.response && error.response.status === 401 && currentPath !== '/login' && !currentPath.startsWith('/reset-password')) {
      logout();
    } else if (error.response && error.response.status === 403 && currentPath !== '/login' && !currentPath.startsWith('/reset-password')) {
      logout();
    }
    return Promise.reject(error);
  }
);


export default instance;