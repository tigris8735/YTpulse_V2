import React from 'react';
import styles from './Button.module.css';

const Button = ({
  children,
  variant = 'primary', // primary, secondary, pro, danger
  size = 'medium', // small, medium, large
  disabled = false,
  onClick,
  className = '',
  type = 'button',
}) => {
  const classes = [
    styles.button,
    styles[variant],
    styles[size],
    disabled && styles.disabled,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classes} onClick={onClick} disabled={disabled} type={type}>
      {children}
    </button>
  );
};

export default Button;