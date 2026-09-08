import api from './axiosConfig';

export const generatePreviews = (data) =>
  api.post('/generate', data).then((res) => res.data);

export const getGenerationStatus = (jobId) =>
  api.get(`/generate/${jobId}`).then((res) => res.data);