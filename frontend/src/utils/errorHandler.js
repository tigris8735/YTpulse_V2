/**
 * Обрабатывает ошибку API и возвращает понятное сообщение
 * @param {any} error - ошибка, пойманная в catch
 * @returns {string} человекочитаемое сообщение
 */
export const getErrorMessage = (error) => {
  // Если ошибка от axios (ответ сервера)
  if (error.response) {
    const status = error.response.status;
    const detail = error.response.data?.detail;

    if (status === 400) return detail || 'Некорректный запрос.';
    if (status === 401) return 'Сессия истекла, войдите заново.';
    if (status === 403) return 'Доступ запрещён. Обновите тариф.';
    if (status === 404) return 'Запрашиваемый ресурс не найден.';
    if (status === 429) return 'Слишком много запросов, подождите немного.';
    if (status >= 500) return 'Внутренняя ошибка сервера, попробуйте позже.';
    return detail || 'Произошла ошибка.';
  }

  // Если ошибка сети (нет ответа)
  if (error.request) {
    return 'Сервер не отвечает. Проверьте подключение к интернету.';
  }

  // Ошибка на стороне клиента
  return error.message || 'Неизвестная ошибка.';
};

/**
 * Оборачивает асинхронную функцию для единообразной обработки ошибок
 * @param {Function} fn - асинхронная функция
 * @param {Function} onError - колбэк при ошибке (получает сообщение)
 * @returns {Function} обёрнутая функция
 */
export const withErrorHandler = (fn, onError) => {
  return async (...args) => {
    try {
      return await fn(...args);
    } catch (error) {
      const message = getErrorMessage(error);
      if (onError) onError(message);
      else console.error('[API Error]', message, error);
      throw error; // пробрасываем дальше, если нужно
    }
  };
};