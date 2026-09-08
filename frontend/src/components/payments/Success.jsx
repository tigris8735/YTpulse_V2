import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Payments.module.css';

const Success = () => {
  const navigate = useNavigate();
  return (
    <div className={styles.result}>
      <div className={styles.icon}>✅</div>
      <h2>Оплата прошла успешно!</h2>
      <p>Ваш тариф Pro активирован.</p>
      <button onClick={() => navigate('/generate')} className={styles.cta}>
        Перейти к генерации
      </button>
    </div>
  );
};

export default Success;