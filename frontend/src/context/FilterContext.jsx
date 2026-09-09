import React, { createContext, useState } from 'react';

export const FilterContext = createContext();

export const FilterProvider = ({ children }) => {
  const [currentFilter, setCurrentFilter] = useState('all');
  const [selectedVideo, setSelectedVideo] = useState(null);

  return (
    <FilterContext.Provider
      value={{ currentFilter, setCurrentFilter, selectedVideo, setSelectedVideo }}
    >
      {children}
    </FilterContext.Provider>
  );
};