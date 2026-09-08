import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../../../context/AuthContext';
import { FilterContext } from '../../../context/FilterContext';
import styles from './Layout.module.css';

const Sidebar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>YT Pulse</div>
      <nav className={styles.nav}>
        <NavLink to="/" className={({ isActive }) => isActive ? styles.active : ''}>
          Тренды США
        </NavLink>
        <NavLink to="/preview" className={({ isActive }) => isActive ? styles.active : ''}>
          Превью
        </NavLink>
        <NavLink to="/generate" className={({ isActive }) => isActive ? styles.active : ''}>
          Генерация
        </NavLink>
        <NavLink to="/queue" className={({ isActive }) => isActive ? styles.active : ''}>
          Очередь
        </NavLink>
        <NavLink to="/cabinet" className={({ isActive }) => isActive ? styles.active : ''}>
          Кабинет
        </NavLink>
      </nav>
      <div className={styles.userInfo}>
        <span>{user?.email}</span>
        <span className={`${styles.plan} ${user?.plan === 'pro' ? styles.pro : styles.free}`}>
          {user?.plan === 'pro' ? 'PRO' : 'FREE'}
        </span>
        <button onClick={handleLogout} className={styles.logoutBtn}>Выйти</button>
      </div>
    </aside>
  );
};

const TopBar = () => {
  const { currentFilter } = useContext(FilterContext);
  return (
    <header className={styles.topbar}>
      <div className={styles.title}>
        <h1>Тренды США</h1>
        <span className={styles.source}>YouTube Most Popular</span>
      </div>
      <button className={styles.refreshBtn}>Обновить кэш</button>
    </header>
  );
};

const BottomBar = () => {
  return (
    <footer className={styles.bottombar}>
      <div className={styles.hint}>Подсказка: выберите видео для разбора</div>
      <div className={styles.actions}>
        <button className={styles.secondary}>Вторичное</button>
        <button className={styles.primary}>Главное действие</button>
      </div>
    </footer>
  );
};

const Layout = () => {
  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.main}>
        <TopBar />
        <div className={styles.content}>
          <Outlet />
        </div>
        <BottomBar />
      </div>
    </div>
  );
};

export default Layout;