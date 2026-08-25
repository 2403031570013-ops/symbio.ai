import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
  timeout: 60000, // Increased to 60 seconds for slower database/email operations
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('symbioai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshPromise = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status;
    const originalRequest = error.config || {};

    const requestUrl = originalRequest.url || '';
    const isAuthenticationRequest = requestUrl.includes('/auth/login')
      || requestUrl.includes('/auth/admin-login')
      || requestUrl.includes('/auth/admin-secret/verify')
      || requestUrl.includes('/auth/google')
      || requestUrl.includes('/auth/refresh');

    if (status === 401 && !originalRequest._retry && !isAuthenticationRequest) {
      originalRequest._retry = true;
      if (!refreshPromise) {
        isRefreshing = true;
        refreshPromise = api.post('/auth/refresh')
          .then((refreshResponse) => {
            const nextToken = refreshResponse?.data?.data?.token;
            if (!nextToken) throw new Error('Missing refreshed access token');
            localStorage.setItem('symbioai_token', nextToken);
            api.defaults.headers.common.Authorization = `Bearer ${nextToken}`;
            return nextToken;
          })
          .catch((refreshError) => {
            localStorage.removeItem('symbioai_token');
            throw refreshError;
          })
          .finally(() => {
            isRefreshing = false;
            refreshPromise = null;
          });
      }

      try {
        const nextToken = await refreshPromise;
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${nextToken}`;
        return api(originalRequest);
      } catch {
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
