import React, { createContext, useState, useEffect, useCallback } from 'react';
import * as authApi from '../api/authApi';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await authApi.login(email, password);
    // data теперь содержит access_token, user_id, email, plan
    const userData = {
      id: data.user_id,
      email: data.email,
      plan: data.plan
    };
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    return data;
  } , []);

  const register = useCallback(async (email, password) => {
    const data = await authApi.register(email, password);
    // После регистрации не логиним автоматически, пусть пользователь войдёт
    return data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};