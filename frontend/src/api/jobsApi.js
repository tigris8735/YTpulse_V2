import api from './axiosConfig';

export const createVideoJob = (data) =>
  api.post('/jobs', data).then((res) => res.data);

export const getJobStatus = (jobId) =>
  api.get(`/jobs/${jobId}`).then((res) => res.data);

export const listJobs = () =>
  api.get('/jobs').then((res) => res.data);