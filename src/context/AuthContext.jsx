import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import api from '../services/api';
import { getApiError } from '../services/response';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('symbioai_token');
    if (!token) {
      setIsAuthLoading(false);
      return;
    }

    api
      .get('/auth/me')
      .then((response) => {
        if (response.data?.success) {
          setUser(response.data.data.user);
          setIsAuthenticated(true);
        } else {
          localStorage.removeItem('symbioai_token');
        }
      })
      .catch(() => {
        localStorage.removeItem('symbioai_token');
        setIsAuthenticated(false);
      })
      .finally(() => {
        setIsAuthLoading(false);
      });
  }, []);

  const login = async (email, password, rememberMe = true) => {
    let response;
    try {
      response = await api.post('/auth/login', { email, password, remember_me: rememberMe });
      if (!response.data?.success) throw new Error(response.data?.message || 'Unable to sign in');
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to sign in'));
    }

    localStorage.setItem('symbioai_token', response.data.data.token);
    setUser(response.data.data.user);
    setIsAuthenticated(true);
    return true;
  };

  const register = async (fullName, email, password, role = 'Waste Producer') => {
    let response;
    try {
      response = await api.post('/auth/register', { full_name: fullName, email, password, role });
      if (!response.data?.success) throw new Error(response.data?.message || 'Unable to create account');
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to create account'));
    }

    return response.data?.data || {};
  };

  const googleLoginWithCredential = async (credential) => {
    let response;
    try {
      response = await api.post('/auth/google', { credential });
      if (!response.data?.success) throw new Error(response.data?.message || 'Unable to sign in with Google');
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to sign in with Google'));
    }

    localStorage.setItem('symbioai_token', response.data.data.token);
    setUser(response.data.data.user);
    setIsAuthenticated(true);
    return true;
  };

  const resetPassword = async (email) => {
    try {
      const response = await api.post('/auth/forgot-password', { email });
      return response.data?.success === true;
    } catch (error) {
      throw new Error(getApiError(error, 'Unable to request password reset'));
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch {
      // Ignore logout failures and clear local state.
    }

    localStorage.removeItem('symbioai_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = useMemo(
    () => ({ user, isAuthenticated, isAuthLoading, login, register, googleLoginWithCredential, resetPassword, logout }),
    [user, isAuthenticated, isAuthLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
