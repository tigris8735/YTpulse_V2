import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { FilterContext } from '../../context/FilterContext';
import { getTrends, refreshCache } from '../../api/trendsApi';
import FilterChips from './FilterChips';
import VideoCard from './VideoCard';
import styles from './Trends.module.css';

const TrendsFeed = () => {
  const { currentFilter, setSelectedVideo } = useContext(FilterContext);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadTrends = async (filter) => {
    setLoading(true);
    try {
      const data = await getTrends(filter);
      console.log('📦 Данные от бэкенда:', data);
      setVideos(data.videos || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadTrends(currentFilter);
  }, [currentFilter]);

  const handleRefresh = async () => {
    await refreshCache();
    await loadTrends(currentFilter);
  };

  const handleCardClick = (video) => {
    if (!video || !video.video_id) return;
    setSelectedVideo(video);
    navigate(`/preview?videoId=${video.video_id}`);
  };

  if (loading) return <div className="loader">Загрузка трендов...</div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <FilterChips />
        <button onClick={handleRefresh} className={styles.refreshBtn}>Обновить кэш</button>
      </div>
      <div className={styles.grid}>
        {videos
          .filter(video => video && typeof video === 'object' && video.video_id && video.title)
          .map((video) => (
            <VideoCard key={video.video_id} video={video} onClick={() => handleCardClick(video)} />
          ))}
      </div>
    </div>
  );
};

export default TrendsFeed;