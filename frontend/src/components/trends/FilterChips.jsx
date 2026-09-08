import React, { useContext } from 'react';
import { FilterContext } from '../../context/FilterContext';
import styles from './Trends.module.css';

const filters = ['All', 'Shorts', 'Longform', 'Gaming', 'AI', 'Finance'];

const FilterChips = () => {
  const { currentFilter, setCurrentFilter } = useContext(FilterContext);

  return (
    <div className={styles.chips}>
      {filters.map((f) => (
        <button
          key={f}
          className={`${styles.chip} ${currentFilter === f ? styles.activeChip : ''}`}
          onClick={() => setCurrentFilter(f)}
        >
          {f}
        </button>
      ))}
    </div>
  );
};

export default FilterChips;