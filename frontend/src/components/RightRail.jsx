import { Bookmark, ChevronRight, Clock3, Bell, MapPin } from 'lucide-react';
import CompanyLogo from './CompanyLogo';
import { useAuth } from '../context/AuthContext';

export default function RightRail({ saved, applications }) {
  const { user } = useAuth();
  return (
    <aside className="right-rail">
      <div className="quote-card"><div>“A small step today<br />can lead to a big opportunity<br />tomorrow.”</div><small>— Keep going!</small><span className="mountain">⚑</span></div>
      <section className="rail-card"><header><h3>Saved Jobs</h3><span>{saved.length ? 'View all' : ''}</span></header>
        {saved.slice(0, 3).map((item) => <div className="rail-job" key={item.id}><CompanyLogo company={item.job.company} size="sm" /><div><b>{item.job.title}</b><p>{item.job.company.name}</p><small><Clock3 size={11} /> Saved recently</small></div><Bookmark size={17} /></div>)}
        {!saved.length && <p className="rail-empty">{user ? 'Jobs you save will appear here.' : 'Sign in to save jobs.'}</p>}
      </section>
      <section className="rail-card"><header><h3>Recent Applications</h3><span>{applications.length ? 'View all' : ''}</span></header>
        {applications.slice(0, 3).map((item) => <div className="rail-job" key={item.id}><CompanyLogo company={item.job.company} size="sm" /><div><b>{item.job.title}</b><p>{item.job.company.name}</p><small className={`status ${item.status}`}><i /> {item.status === 'interviewing' ? 'Under Review' : 'Applied'}</small></div></div>)}
        {!applications.length && <p className="rail-empty">Apply to jobs and they will show here.</p>}
      </section>
      <section className="alert-card"><div className="alert-icon"><Bell size={21} /></div><div><h3>Job Alerts</h3><p>Get notified about new jobs matching your preferences.</p></div><ChevronRight size={20} /></section>
    </aside>
  );
}
