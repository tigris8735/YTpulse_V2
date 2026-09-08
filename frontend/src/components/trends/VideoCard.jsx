import React from 'react';
import styles from './Trends.module.css';

const VideoCard = ({ video, onClick }) => {
  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.thumbnail}>
        <img
          src={`https://i.ytimg.com/vi/${video.id}/mqdefault.jpg`}
          alt={video.snippet.title}
          loading="lazy"
        />
        <span className={styles.duration}>{video.contentDetails?.duration || 'N/A'}</span>
      </div>
      <div className={styles.info}>
        <h3>{video.snippet.title}</h3>
        <p>{video.snippet.channelTitle}</p>
        <div className={styles.meta}>
          <span>{video.statistics?.viewCount?.toLocaleString() || 0} просмотров</span>
        </div>
      </div>
    </div>
  );
};

export default VideoCard;