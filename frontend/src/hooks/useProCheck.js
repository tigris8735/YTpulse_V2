import { useAuth } from './useAuth';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

/**
 * Хук для проверки Pro-доступа и редиректа на тарифы, если нет подписки
 * @param {string} redirectTo - путь для редиректа (по умолчанию '/plans')
 * @returns {Object} { isPro, loading } - статус Pro и загрузка
 */
export const useProCheck = (redirectTo = '/plans') => {
  const { user, loading, isPro } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isPro) {
      navigate(redirectTo, { replace: true });
    }
  }, [loading, isPro, navigate, redirectTo]);

  return { isPro, loading };
};