import React, { useState, useEffect, useContext } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FilterContext } from '../../context/FilterContext';
import { AuthContext } from '../../context/AuthContext';
import { getPreview } from '../../api/previewApi';
import styles from './Preview.module.css';

const PreviewPage = () => {
  const [searchParams] = useSearchParams();
  const videoId = searchParams.get('videoId');
  const { selectedVideo } = useContext(FilterContext);
  const { user } = useContext(AuthContext);
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!videoId) return;
    const fetchPreview = async () => {
      setLoading(true);
      try {
        const data = await getPreview(videoId);
        setPreviewData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPreview();
  }, [videoId]);

  if (loading) return <div className="loader">Загрузка превью...</div>;
  if (!previewData) return <div>Превью не найдено</div>;

  const tags = [
    { label: 'Face closeup', value: previewData.face_closeup },
    { label: 'High contrast', value: previewData.high_contrast },
    { label: 'Text area', value: previewData.text_area },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.list}>
        <h3>Top performing previews</h3>
        <ul>
          {/* Здесь должен быть список отсортированных превью, но для примера просто текущий */}
          <li className={styles.listItem}>
            <img src={`https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`} alt="" />
            <span>{selectedVideo?.snippet?.title || 'Video'}</span>
          </li>
        </ul>
      </div>
      <div className={styles.center}>
        <img
          src={`https://i.ytimg.com/vi/${videoId}/maxresdefault.jpg`}
          alt="preview"
          className={styles.previewImage}
        />
      </div>
      <div className={styles.rail}>
        <h4>Why it clicks</h4>
        {tags.map((tag) => (
          <div key={tag.label} className={styles.tag}>
            <span className={tag.value ? styles.pass : styles.fail}>
              {tag.value ? '✅' : '❌'}
            </span>
            <span>{tag.label}</span>
          </div>
        ))}
        <div className={styles.actions}>
          {user?.plan === 'pro' ? (
            <button className={styles.generateBtn}>Сгенерировать пак</button>
          ) : (
            <button className={styles.upgradeBtn}>Открыть Pro</button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PreviewPage;