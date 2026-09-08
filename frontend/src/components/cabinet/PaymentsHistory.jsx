import React, { useState, useEffect } from 'react';
import api from '../../api/axiosConfig';
import styles from './Cabinet.module.css';

const PaymentsHistory = () => {
  const [payments, setPayments] = useState([]);

  useEffect(() => {
    const fetchPayments = async () => {
      try {
        const res = await api.get('/payments/history');
        setPayments(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchPayments();
  }, []);

  return (
    <div className={styles.section}>
      <h3>Платежи</h3>
      <table className={styles.paymentTable}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Срок</th>
            <th>Сумма</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {payments.map((p) => (
            <tr key={p.id}>
              <td>{p.yookassa_id}</td>
              <td>{p.term}</td>
              <td>{p.amount} ₽</td>
              <td>{p.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PaymentsHistory;