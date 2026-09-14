import { useEffect, useState } from 'react';

const pills = [['', 'All Jobs'], ['remote', 'Remote'], ['full-time', 'Full Time'], ['part-time', 'Part Time'], ['internship', 'Internship'], ['contract', 'Contract']];

export default function SearchFilters({ onFilter, initialFilters }) {
  const [filters, setFilters] = useState(initialFilters);
  useEffect(() => setFilters(initialFilters), [initialFilters]);

  const setType = (job_type) => {
    const next = { ...filters, job_type };
    setFilters(next); onFilter(next);
  };
  return (
    <div className="filter-bar">
      <div className="filter-pills">
        {pills.map(([value, label]) => (
          <button key={label} className={(value === 'remote' ? filters.remote : filters.job_type === value) ? 'selected' : ''} onClick={() => value === 'remote' ? (() => { const next = { ...filters, remote: !filters.remote }; setFilters(next); onFilter(next); })() : setType(value)}>{label}</button>
        ))}
      </div>
      <select value={filters.experience} onChange={(e) => { const next = { ...filters, experience: e.target.value }; setFilters(next); onFilter(next); }}>
        <option value="">Most Relevant</option>
        <option value="entry">Entry Level</option><option value="intern">Intern</option><option value="mid">Mid Level</option><option value="senior">Senior</option>
      </select>
    </div>
  );
}
