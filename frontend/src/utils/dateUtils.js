/**
 * Форматирует дату в локальный строковый формат
 * @param {string|Date} date - дата в формате ISO или объект Date
 * @param {string} locale - локаль (по умолчанию 'ru-RU')
 * @returns {string} отформатированная дата
 */
export const formatDate = (date, locale = 'ru-RU') => {
  if (!date) return '—';
  const d = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Возвращает разницу между двумя датами в днях
 * @param {string|Date} start - начальная дата
 * @param {string|Date} end - конечная дата (по умолчанию текущая)
 * @returns {number} количество дней (может быть отрицательным, если end раньше start)
 */
export const daysBetween = (start, end = new Date()) => {
  const startDate = typeof start === 'string' ? new Date(start) : start;
  const endDate = typeof end === 'string' ? new Date(end) : end;
  const diffMs = endDate.getTime() - startDate.getTime();
  return Math.floor(diffMs / (1000 * 60 * 60 * 24));
};

/**
 * Проверяет, активна ли Pro-подписка
 * @param {string|null} proExpiresAt - дата окончания Pro в ISO
 * @returns {boolean}
 */
export const isProActive = (proExpiresAt) => {
  if (!proExpiresAt) return false;
  const exp = new Date(proExpiresAt);
  const now = new Date();
  return exp > now;
};

/**
 * Форматирует сумму в рубли с символом ₽
 * @param {number} amount - сумма
 * @returns {string}
 */
export const formatPrice = (amount) => {
  return `${amount.toLocaleString()} ₽`;
};