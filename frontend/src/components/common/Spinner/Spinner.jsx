import React from 'react';
import styles from './Spinner.module.css';

const Spinner = ({ size = 'medium' }) => {
  return <div className={`${styles.spinner} ${styles[size]}`}></div>;
};

export default Spinner;