import React from 'react';
import styles from './Cabinet.module.css';

const features = [
  { name: 'Лента US трендов', free: true, pro: true },
  { name: 'Фильтры', free: true, pro: true },
  { name: 'Why it clicks (локальный разбор)', free: true, pro: true },
  { name: 'Генерация превью', free: false, pro: true },
  { name: 'Очередь ролика', free: false, pro: true },
];

const Features = ({ user }) => {
  return (
    <div className={styles.section}>
      <h3>Возможности</h3>
      <ul className={styles.featureList}>
        {features.map((f) => (
          <li key={f.name}>
            <span>{f.name}</span>
            <span className={f.pro ? styles.proBadge : styles.freeBadge}>
              {f.pro ? 'Pro' : 'Free'}
            </span>
            {user?.plan === 'free' && !f.free && (
              <span className={styles.locked}>🔒</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Features;