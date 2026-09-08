import api from './axiosConfig';

export const getTrends = (filter = 'All') =>
  api.get('/trends', { params: { filter } }).then((res) => res.data);

export const refreshCache = () =>
  api.post('/trends/refresh').then((res) => res.data);