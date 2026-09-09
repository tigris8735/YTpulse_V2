import React from 'react';

const VideoCard = ({ video, onClick }) => {
  if (!video) return null;
  return (
    <div onClick={onClick} style={{ border: '1px solid #ccc', padding: '10px', margin: '5px' }}>
      <h3>{video.title || 'Без названия'}</h3>
      <p>{video.channel_title || 'Неизвестный канал'}</p>
    </div>
  );
};

export default VideoCard;