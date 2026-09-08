import api from './axiosConfig';

export const createPayment = (term) =>
  api.post('/payments/create', { term }).then((res) => res.data);