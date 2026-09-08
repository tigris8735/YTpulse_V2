import React from 'react';
import styles from './Card.module.css';

const Card = ({ children, className = '', selected = false, onClick }) => {
  return (
    <div
      className={`${styles.card} ${selected ? styles.selected : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;