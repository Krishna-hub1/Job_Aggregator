import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Trash2 } from 'lucide-react';
import { api } from '../services/api';
import CompanyLogo from '../components/CompanyLogo';

export default function SavedJobs() {
  const [saved, setSaved] = useState([]); const [loading, setLoading] = useState(true);
  const load = () => api.getSavedJobs().then(({ data }) => setSaved(data)).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);
  const remove = async (id) => { await api.deleteSavedJob(id); setSaved(saved.filter(x => x.id !== id)); };
  if (loading) return <div className="page-card">Loading saved jobs...</div>;
  return <div className="simple-page"><div className="page-heading"><div><p>YOUR JOBS</p><h1>Saved Jobs</h1><span>Keep your best opportunities in one place.</span></div><Link to="/" className="apply-now">Browse jobs</Link></div>{!saved.length ? <div className="page-card empty-large">No saved jobs yet. <Link to="/">Browse jobs</Link> and bookmark the ones you like.</div> : <div className="saved-grid">{saved.map(item => <article className="saved-card" key={item.id}><CompanyLogo company={item.job.company}/><div><h3>{item.job.title}</h3><p>{item.job.company.name}</p><small>{item.job.location || 'Location not specified'} · {item.status}</small></div><div><button className="save-icon" onClick={() => remove(item.id)}><Trash2 size={19}/></button><a href={item.job.apply_url} target="_blank" rel="noreferrer" className="apply-now">Apply</a></div></article>)}</div>}</div>;
}
