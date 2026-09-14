import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import SearchFilters from '../components/SearchFilters';
import JobList from '../components/JobList';
import RightRail from '../components/RightRail';

const EMPTY_FILTERS = { search: '', location: '', job_type: '', experience: '', remote: false };

export default function Home({ globalSearch = '', globalLocation = { country: '', location: '' } }) {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]); const [loading, setLoading] = useState(true); const [error, setError] = useState(''); const [filters, setFilters] = useState(EMPTY_FILTERS); const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 0 }); const [saved, setSaved] = useState([]); const [heroSearch, setHeroSearch] = useState('');

  const fetchJobs = useCallback(async (params = {}) => { setLoading(true); setError(''); try { const { data } = await api.getJobs({ ...filters, ...params }); setJobs(data.jobs || []); setPagination({ page: data.current_page, total: data.total, pages: data.pages, hasNext: data.has_next, hasPrev: data.has_prev }); } catch { setError('Could not load jobs. Make sure Flask is running on port 5000.'); } finally { setLoading(false); } }, [filters]);

  useEffect(() => { fetchJobs({ page: 1 }); }, [fetchJobs]);
  useEffect(() => { if (globalSearch !== undefined && globalSearch !== heroSearch) { const next = { ...filters, search: globalSearch }; setHeroSearch(globalSearch); setFilters(next); } }, [globalSearch]);
  useEffect(() => { if (globalLocation) { const next = { ...filters, country: globalLocation.country || '', location: globalLocation.location || '' }; setFilters(next); } }, [globalLocation.country, globalLocation.location]);
  useEffect(() => { if (user) api.getSavedJobs().then(({ data }) => setSaved(data)).catch(() => setSaved([])); else setSaved([]); }, [user]);

  const savedIds = useMemo(() => new Set(saved.map(x => x.job.id)), [saved]);
  const applications = useMemo(() => saved.filter(x => ['applied', 'interviewing', 'offer'].includes(x.status)), [saved]);

  const search = (value) => { const next = { ...filters, search: value }; setHeroSearch(value); setFilters(next); };
  const handleFilter = (next) => setFilters(next);
  const handleSave = async (id) => { if (!user) { window.location.href = '/login'; return; } try { await api.saveJob(id); const { data } = await api.getSavedJobs(); setSaved(data); } catch { /* keep UI quiet */ } };
  const handleApply = async (job, needsLogin) => { if (needsLogin) { window.location.href = '/login'; return; } try { await api.applyJob(job.id); const { data } = await api.getSavedJobs(); setSaved(data); } catch { /* external apply still opened */ } };

  return <div className="dashboard-grid"><main className="dashboard-main">
    <section className="hero-banner"><div className="hero-copy"><h1>Find Your<br />Next <span>Opportunity</span></h1><p>We aggregate jobs from top companies across the web<br />to help you find the right fit — faster.</p><div className="popular"><b>Popular searches:</b>{['Python', 'Frontend', 'Remote', 'Data Analyst', 'Internship'].map(x => <button key={x} onClick={() => search(x)}>{x}</button>)}</div></div><div className="hero-art"><div className="plant">🌿</div><div className="person-head"/><div className="person-body"/><div className="laptop"/><div className="hero-scribble">Better<br/>Jobs<br/><i>Brighter<br/>Future</i></div></div></section>
    <SearchFilters onFilter={handleFilter} initialFilters={filters} />
    {error && <div className="error-banner">{error}</div>}
    <div className="results-header"><div><strong>{pagination.total.toLocaleString()}</strong> jobs found</div><span>Fresh listings from our job sources</span></div>
    <JobList jobs={jobs} loading={loading} onSave={handleSave} onApply={handleApply} savedIds={savedIds}/>
    {pagination.pages > 1 && <div className="pagination"><button disabled={!pagination.hasPrev} onClick={() => fetchJobs({ page: pagination.page - 1 })}>Previous</button><span>Page {pagination.page} of {pagination.pages}</span><button disabled={!pagination.hasNext} onClick={() => fetchJobs({ page: pagination.page + 1 })}>Next</button></div>}
  </main><RightRail saved={saved} applications={applications}/></div>;
}
