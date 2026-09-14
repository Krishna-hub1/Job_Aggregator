import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [tab, setTab] = useState('overview');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true); setMessage('');
    try {
      const [s, u, j] = await Promise.all([api.adminDashboard(), api.adminUsers(), api.adminJobs()]);
      setStats(s.data); setUsers(u.data); setJobs(j.data);
    } catch (e) { setMessage(e.response?.data?.message || 'Unable to load admin data.'); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const toggleUser = async (u) => {
    try { await api.adminUpdateUser(u.id, { is_active: !u.is_active }); await load(); }
    catch (e) { setMessage(e.response?.data?.message || 'Unable to update user.'); }
  };
  const toggleJob = async (job) => {
    try { await api.adminUpdateJob(job.id, { is_active: !job.is_active }); await load(); }
    catch (e) { setMessage(e.response?.data?.message || 'Unable to update job.'); }
  };
  const scrape = async () => {
    setMessage('Scraping jobs...');
    try { const r = await api.adminScrape(); setMessage(`Scrape completed: ${r.data?.message || 'jobs updated'}`); await load(); }
    catch (e) { setMessage(e.response?.data?.message || e.response?.data?.error || 'Scrape failed.'); }
  };

  if (user?.role !== 'admin') return <div className="admin-page"><h1>Access denied</h1><p>Admin access is required.</p></div>;
  if (loading && !stats) return <div className="admin-page"><h1>Admin Dashboard</h1><p>Loading...</p></div>;

  return <div className="admin-page">
    <div className="admin-header"><div><span className="eyebrow">ADMINISTRATION</span><h1>Admin Dashboard</h1><p>Manage users, jobs and the job aggregation process.</p></div><button className="admin-primary" onClick={scrape}>Run job scraper</button></div>
    {message && <div className="admin-message">{message}</div>}
    <div className="admin-tabs">{[['overview','Overview'],['users','Users'],['jobs','Jobs']].map(([id,label]) => <button key={id} className={tab===id?'active':''} onClick={()=>setTab(id)}>{label}</button>)}</div>
    {tab==='overview' && <>
      <div className="admin-stats">{[['Users',stats?.users],['Active users',stats?.active_users],['Jobs',stats?.jobs],['Active jobs',stats?.active_jobs],['Companies',stats?.companies],['Applications',stats?.applications]].map(([label,value])=><div className="admin-stat" key={label}><small>{label}</small><strong>{value ?? 0}</strong></div>)}</div>
      <div className="admin-card"><h2>Admin responsibilities</h2><ul><li>Monitor platform users and disable abusive/inactive accounts.</li><li>Review and hide jobs that should no longer appear to users.</li><li>Trigger the Greenhouse and Lever scrapers manually.</li><li>Monitor job, company and application totals.</li></ul></div>
    </>}
    {tab==='users' && <div className="admin-card"><div className="admin-card-title"><h2>Users</h2><span>{users.length} accounts</span></div><div className="admin-table-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Action</th></tr></thead><tbody>{users.map(u=><tr key={u.id}><td>{u.name}</td><td>{u.email}</td><td>{u.role}</td><td><span className={`status ${u.is_active?'on':'off'}`}>{u.is_active?'Active':'Disabled'}</span></td><td><button className="table-button" disabled={u.id===user.id} onClick={()=>toggleUser(u)}>{u.is_active?'Disable':'Enable'}</button></td></tr>)}</tbody></table></div></div>}
    {tab==='jobs' && <div className="admin-card"><div className="admin-card-title"><h2>Jobs</h2><span>{jobs.length} shown</span></div><div className="admin-table-wrap"><table><thead><tr><th>Title</th><th>Company</th><th>Location</th><th>Status</th><th>Action</th></tr></thead><tbody>{jobs.map(j=><tr key={j.id}><td>{j.title}</td><td>{j.company?.name}</td><td>{j.location || '—'}</td><td><span className={`status ${j.is_active?'on':'off'}`}>{j.is_active?'Active':'Hidden'}</span></td><td><button className="table-button" onClick={()=>toggleJob(j)}>{j.is_active?'Hide':'Publish'}</button></td></tr>)}</tbody></table></div></div>}
  </div>;
}
