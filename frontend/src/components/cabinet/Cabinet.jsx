import React, { useContext } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import Profile from './Profile';
import Subscription from './Subscription';
import Features from './Features';
import PaymentsHistory from './PaymentsHistory';
import styles from './Cabinet.module.css';

const Cabinet = () => {
  const { user } = useContext(AuthContext);
  const location = useLocation();

  const tabs = [
    { path: '/cabinet', label: 'Профиль' },
    { path: '/cabinet/subscription', label: 'Подписка' },
    { path: '/cabinet/features', label: 'Возможности' },
    { path: '/cabinet/payments', label: 'Платежи' },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.tabs}>
        {tabs.map((tab) => (
          <Link
            key={tab.path}
            to={tab.path}
            className={`${styles.tab} ${location.pathname === tab.path ? styles.activeTab : ''}`}
          >
            {tab.label}
          </Link>
        ))}
      </div>
      <div className={styles.content}>
        <Routes>
          <Route index element={<Profile user={user} />} />
          <Route path="subscription" element={<Subscription user={user} />} />
          <Route path="features" element={<Features user={user} />} />
          <Route path="payments" element={<PaymentsHistory />} />
        </Routes>
      </div>
    </div>
  );
};

export default Cabinet;