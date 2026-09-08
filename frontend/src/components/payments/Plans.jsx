import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createPayment } from '../../api/paymentsApi';
import styles from './Payments.module.css';

const plans = [
  { id: 'free', label: 'Free', price: 0, term: 'бессрочно', features: ['Лента US', 'Фильтры', 'Why it clicks'] },
  { id: 'month', label: 'Pro месяц', price: 700, term: '1 месяц', features: ['Всё Free', 'Генерация превью', 'Очередь ролика'], highlight: true },
  { id: 'half', label: 'Pro 6 мес', price: 1800, term: '6 месяцев', features: ['Всё Free', 'Генерация превью', 'Очередь ролика'] },
  { id: 'year', label: 'Pro год', price: 7000, term: '1 год', features: ['Всё Free', 'Генерация превью', 'Очередь ролика'] },
];

const Plans = () => {
  const navigate = useNavigate();
  const [selectedTerm, setSelectedTerm] = useState(null);

  const handleSelect = (plan) => {
    if (plan.id === 'free') {
      navigate('/');
      return;
    }
    setSelectedTerm(plan.id);
    // Переход на страницу оплаты с параметром
    navigate(`/checkout?term=${plan.id}`);
  };

  return (
    <div className={styles.container}>
      <h2>Тарифы</h2>
      <div className={styles.grid}>
        {plans.map((plan) => (
          <div key={plan.id} className={`${styles.card} ${plan.highlight ? styles.highlight : ''}`}>
            <h3>{plan.label}</h3>
            <div className={styles.price}>{plan.price} ₽</div>
            <div className={styles.term}>{plan.term}</div>
            <ul className={styles.features}>
              {plan.features.map((f) => <li key={f}>{f}</li>)}
            </ul>
            {plan.id !== 'free' && <div className={styles.testBadge}>TEST MODE</div>}
            <button
              className={styles.selectBtn}
              onClick={() => handleSelect(plan)}
            >
              {plan.id === 'free' ? 'Выбрать' : 'Купить'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Plans;