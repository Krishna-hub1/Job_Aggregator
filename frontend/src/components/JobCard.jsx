import { Bookmark, Clock3, MapPin, BriefcaseBusiness, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import CompanyLogo from './CompanyLogo';
import { useAuth } from '../context/AuthContext';

export default function JobCard({ job, onSave, onApply, saved }) {
  const { user } = useAuth();
  const typeLabel = job.job_type ? job.job_type.replace('-', ' ') : 'Full Time';
  const experience = job.experience_level ? job.experience_level.replace(/^./, (c) => c.toUpperCase()) : '0–2 years';
  const posted = job.posted_at ? new Date(job.posted_at).toLocaleDateString(undefined, { day: 'numeric', month: 'short' }) : 'Recently';

  const apply = () => {
    if (!user) {
      onApply?.(job, true);
      return;
    }
    window.open(job.apply_url, '_blank', 'noopener,noreferrer');
    onApply?.(job, false);
  };

  return (
    <article className="job-row">
      <CompanyLogo company={job.company} />
      <div className="job-main">
        <div className="job-title-line">
          <div><Link className="job-title-link" to={`/jobs/${job.id}`}><h3>{job.title}</h3></Link><p>{job.company.name}</p></div>
          <span className="posted">Posted {posted}</span>
        </div>
        <div className="job-info">
          <span><MapPin size={14} /> {job.location || 'Location not specified'}</span>
          <em>•</em><span><BriefcaseBusiness size={14} /> {typeLabel}</span>
          <em>•</em><span><Clock3 size={14} /> {experience}</span>
        </div>
        <div className="tag-row">
          {[job.title?.includes('Python') && 'Python', job.title?.includes('Frontend') && 'React', job.experience_level === 'entry' && 'Problem Solving', job.remote && 'Remote'].filter(Boolean).slice(0, 4).map((tag) => <span key={tag}>{tag}</span>)}
          {!job.remote && job.description && <span>+2</span>}
        </div>
      </div>
      <div className="job-actions">
        <button className={`save-icon ${saved ? 'saved' : ''}`} title={saved ? 'Saved' : 'Save job'} onClick={() => onSave(job.id)}><Bookmark size={20} fill={saved ? 'currentColor' : 'none'} /></button>
        <button className="apply-now" onClick={apply}>Apply Now <ExternalLink size={14} /></button>
      </div>
    </article>
  );
}
