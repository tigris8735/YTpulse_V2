import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

/**
 * Кастомный хук для работы с аутентификацией
 * @returns {Object} { user, loading, login, register, logout, isPro }
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth должен использоваться внутри AuthProvider');
  }

  const { user, loading, login, register, logout } = context;

  // Дополнительное вычисление isPro
  const isPro = user?.plan === 'pro';

  return { user, loading, login, register, logout, isPro };
};