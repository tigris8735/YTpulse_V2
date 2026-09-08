import api from './axiosConfig';

export const getPreview = (videoId) =>
  api.get(`/preview/${videoId}`).then((res) => res.data);

// Для списка трендов уже обогащённых тегами, отдельный эндпоинт не требуется,
// т.к. /trends возвращает preview_tags.