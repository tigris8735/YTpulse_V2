import React from 'react';
import styles from './Trends.module.css';

const VideoCard = ({ video, onClick }) => {
  // Если видео нет – ничего не рендерим
  if (!video) return null;

  // Безопасное чтение полей (используем поля из бэкенда)
  const title = video.title || 'Без названия';
  const channel = video.channel_title || 'Неизвестный канал';
  const thumbnail = video.thumbnail || '';
  const views = video.views ? Number(video.views).toLocaleString() : '0';
  const duration = video.duration ? formatDuration(video.duration) : 'N/A';

  // Функция форматирования длительности (секунды -> MM:SS или HH:MM:SS)
  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.thumbnail}>
        <img
          src={thumbnail}
          alt={title}
          loading="lazy"
        />
        <span className={styles.duration}>{duration}</span>
      </div>
      <div className={styles.info}>
        <h3>{title}</h3>
        <p>{channel}</p>
        <div className={styles.meta}>
          <span>{views} просмотров</span>
        </div>
      </div>
    </div>
  );
};

export default VideoCard;