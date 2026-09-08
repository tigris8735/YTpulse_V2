import { useState, useEffect } from 'react';
import { getErrorMessage } from '../utils/errorHandler';

/**
 * Хук для выполнения асинхронного запроса с управлением состоянием
 * @param {Function} fetchFn - асинхронная функция, возвращающая промис
 * @param {Array} deps - зависимости для повторного вызова (useEffect)
 * @param {boolean} immediate - выполнять сразу (по умолчанию true)
 * @returns {Object} { data, loading, error, refetch }
 */
export const useFetch = (fetchFn, deps = [], immediate = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      console.error('[useFetch]', message, err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (immediate) {
      fetchData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { data, loading, error, refetch: fetchData };
};