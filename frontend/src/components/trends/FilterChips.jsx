import React, { useContext } from 'react';
import { FilterContext } from '../../context/FilterContext';
import styles from './Trends.module.css';

const filters = ['all', 'shorts', 'longform', 'gaming', 'ai', 'finance'];

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