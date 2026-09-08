import React, { useState, useEffect } from 'react';
import { listJobs } from '../../api/jobsApi';
import styles from './Queue.module.css';

const QueuePage = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await listJobs();
        setJobs(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
    const interval = setInterval(fetchJobs, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loader">Загрузка задач...</div>;

  return (
    <div className={styles.container}>
      <h3>Очередь ролика</h3>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Тип</th>
            <th>Статус</th>
            <th>Файл</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id}>
              <td>{job.id}</td>
              <td>{job.type}</td>
              <td>
                <span className={`${styles.status} ${styles[job.status]}`}>
                  {job.status}
                </span>
              </td>
              <td>
                {job.status === 'ready' && job.file_url ? (
                  <video controls width="200" className={styles.player}>
                    <source src={job.file_url} type="video/mp4" />
                  </video>
                ) : (
                  '—'
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default QueuePage;