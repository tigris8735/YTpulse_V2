import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { createPayment } from '../../api/paymentsApi';
import styles from './Payments.module.css';

const Checkout = () => {
  const [searchParams] = useSearchParams();
  const term = searchParams.get('term');
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [paymentUrl, setPaymentUrl] = useState(null);

  useEffect(() => {
    if (!term) {
      navigate('/plans');
      return;
    }
    const initPayment = async () => {
      setLoading(true);
      try {
        const data = await createPayment(term);
        // data: { payment_url, payment_id }
        setPaymentUrl(data.payment_url);
        // Если нужно перенаправить на ЮKassa автоматически
        window.location.href = data.payment_url;
      } catch (err) {
        console.error(err);
        navigate('/payment/error');
      } finally {
        setLoading(false);
      }
    };
    initPayment();
  }, [term, navigate]);

  if (loading) return <div className="loader">Создание платежа...</div>;

  return <div className={styles.checkout}>Перенаправление на оплату...</div>;
};

export default Checkout;