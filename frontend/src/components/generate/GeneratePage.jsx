import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generatePreviews } from '../../api/generateApi';
import styles from './Generate.module.css';

const GeneratePage = () => {
  const [topic, setTopic] = useState('');
  const [count, setCount] = useState(3);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [results, setResults] = useState([]);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await generatePreviews({ topic, count });
      setJobId(data.job_id);
      // Для прототипа сразу заполняем результаты (заглушка)
      setResults(data.images || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleQueue = () => {
    navigate('/queue');
  };

  return (
    <div className={styles.container}>
      <div className={styles.form}>
        <h3>Генерация пака превью</h3>
        <form onSubmit={handleSubmit}>
          <label>Тема / тренд</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Введите тему"
            required
          />
          <label>Количество вариантов</label>
          <select value={count} onChange={(e) => setCount(Number(e.target.value))}>
            <option value={1}>1</option>
            <option value={2}>2</option>
            <option value={3}>3</option>
          </select>
          <button type="submit" disabled={loading} className={styles.primary}>
            {loading ? 'Генерация...' : 'Сгенерировать'}
          </button>
        </form>
        {jobId && (
          <div className={styles.status}>
            Статус: <span className={styles.queued}>queued</span> → rendering → ready
          </div>
        )}
        <button onClick={handleQueue} className={styles.queueBtn}>
          Поставить ролик в очередь
        </button>
      </div>
      <div className={styles.gallery}>
        {results.length > 0 && (
          <div className={styles.grid}>
            {results.map((img, idx) => (
              <div key={idx} className={styles.resultCard}>
                <img src={img} alt={`Вариант ${idx+1}`} />
              </div>
            ))}
          </div>
        )}
        {loading && <div className="loader">Генерация...</div>}
        {!results.length && !loading && <div className={styles.placeholder}>Здесь будут варианты</div>}
      </div>
    </div>
  );
};

export default GeneratePage;