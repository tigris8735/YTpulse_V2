import React from 'react';
import styles from './Cabinet.module.css';

const Subscription = ({ user }) => {
  return (
    <div className={styles.section}>
      <h3>Подписка</h3>
      <p><strong>Текущий план:</strong> {user?.plan === 'pro' ? 'Pro' : 'Free'}</p>
      <p><strong>Начало:</strong> {user?.pro_expires_at ? '—' : '—'}</p>
      <p><strong>Окончание:</strong> {user?.pro_expires_at ? new Date(user.pro_expires_at).toLocaleDateString() : '—'}</p>
      <p className={styles.testBadge}>Тестовый платёж, автопродления нет</p>
    </div>
  );
};

export default Subscription;