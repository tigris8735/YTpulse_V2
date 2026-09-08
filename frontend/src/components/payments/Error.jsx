import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Payments.module.css';

const ErrorPage = () => {
  const navigate = useNavigate();
  return (
    <div className={styles.result}>
      <div className={styles.icon}>❌</div>
      <h2>Оплата не завершена</h2>
      <p>Попробуйте снова или выберите другой тариф.</p>
      <button onClick={() => navigate('/plans')} className={styles.cta}>
        Вернуться к тарифам
      </button>
    </div>
  );
};

export default ErrorPage;