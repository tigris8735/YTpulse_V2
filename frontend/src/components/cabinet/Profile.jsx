import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import styles from './Cabinet.module.css';

const Profile = ({ user }) => {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className={styles.section}>
      <h3>Профиль</h3>
      <p><strong>Email:</strong> {user?.email}</p>
      <p><strong>План:</strong> {user?.plan === 'pro' ? 'Pro' : 'Free'}</p>
      <p><strong>Pro истекает:</strong> {user?.pro_expires_at ? new Date(user.pro_expires_at).toLocaleDateString() : '—'}</p>
      <div className={styles.actions}>
        <button onClick={handleLogout} className={styles.logout}>Выйти</button>
        <button className={styles.manage}>Управлять подпиской</button>
      </div>
    </div>
  );
};

export default Profile;