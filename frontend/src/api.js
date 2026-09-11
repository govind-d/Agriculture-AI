import axios from 'axios';

// Create an Axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Request interceptor to add the auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth endpoints report bad credentials with 401 themselves — never refresh for them
const AUTH_PATHS = ['/api/auth/login', '/api/auth/register', '/api/auth/refresh'];

// Requests that fail together (e.g. weather current + forecast) share one refresh call
let refreshPromise = null;

const endSession = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  window.dispatchEvent(new Event('auth-expired'));
  if (window.location.pathname !== '/login') {
    window.location.assign('/login');
  }
};

// Response interceptor: on an expired access token, get a new one with the
// refresh token and retry once; if that isn't possible, send the user to login
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    // 401 = expired/invalid token; 403 "Not authenticated" = no token was sent
    const isAuthError =
      status === 401 || (status === 403 && error.response?.data?.detail === 'Not authenticated');

    if (!isAuthError || !original || AUTH_PATHS.some((p) => original.url?.startsWith(p))) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem('refreshToken');
    if (original._retried || !refreshToken) {
      endSession();
      return Promise.reject(error);
    }

    try {
      if (!refreshPromise) {
        refreshPromise = api
          .post('/api/auth/refresh', { refreshToken })
          .then((res) => {
            localStorage.setItem('token', res.data.accessToken);
            return res.data.accessToken;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }
      const token = await refreshPromise;
      original._retried = true;
      original.headers.Authorization = `Bearer ${token}`;
      return api(original);
    } catch {
      endSession();
      return Promise.reject(error);
    }
  }
);

export default api;
