import api from './axiosConfig';

export const register = (email, password) =>
  api.post('/auth/register', { email, password }).then((res) => res.data);

export const login = (email, password) =>
  api.post('/auth/login', { email, password }).then((res) => res.data);