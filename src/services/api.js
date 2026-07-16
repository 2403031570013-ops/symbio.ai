import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
  // A failed network connection must never leave a form in a permanent loading state.
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('symbioai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshQueue = [];

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status;
    const originalRequest = error.config || {};

    const requestUrl = originalRequest.url || '';
    const isAuthenticationRequest = requestUrl.includes('/auth/login')
      || requestUrl.includes('/auth/admin-login')
      || requestUrl.includes('/auth/google')
      || requestUrl.includes('/auth/refresh');

    // Login and refresh failures are final. Retrying either through the refresh
    // endpoint caused a 401 refresh loop and left the login button on "Signing in...".
    if (status === 401 && !originalRequest._retry && !isAuthenticationRequest) {
      originalRequest._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const refreshResponse = await api.post('/auth/refresh');
          const nextToken = refreshResponse?.data?.data?.token;
          if (!nextToken) throw new Error('Missing refreshed access token');

          localStorage.setItem('symbioai_token', nextToken);
          api.defaults.headers.common.Authorization = `Bearer ${nextToken}`;
          refreshQueue.forEach((cb) => cb(null, nextToken));
          refreshQueue = [];
        } catch (refreshError) {
          refreshQueue.forEach((cb) => cb(refreshError));
          refreshQueue = [];
          localStorage.removeItem('symbioai_token');
          isRefreshing = false;
          return Promise.reject(error);
        }
        isRefreshing = false;
      }

      return new Promise((resolve, reject) => {
        refreshQueue.push((queueError, nextToken) => {
          if (queueError || !nextToken) {
            reject(queueError || error);
            return;
          }
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${nextToken}`;
          resolve(api(originalRequest));
        });
      });
    }

    return Promise.reject(error);
  }
);

export default api;
