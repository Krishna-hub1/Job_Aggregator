import JobCard from './JobCard';

export default function JobList({ jobs, loading, onSave, onApply, savedIds }) {
  if (loading) return <div className="loading-card">Loading fresh jobs...</div>;
  if (!jobs.length) return <div className="no-results">No jobs found. Try changing your search or filters.</div>;
  return <div className="job-list">{jobs.map((job) => <JobCard key={job.id} job={job} onSave={onSave} onApply={onApply} saved={savedIds?.has(job.id)} />)}</div>;
}
