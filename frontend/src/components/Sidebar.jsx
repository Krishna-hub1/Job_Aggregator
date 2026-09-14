import { NavLink, Link } from 'react-router-dom';
import { Home, Search, Bookmark, FileCheck2, UserRound, FileText, Bell, Building2, BookOpen, Rocket, ArrowRight } from 'lucide-react';

const items = [
  ['/', 'Home', Home],
  ['/browse', 'Browse Jobs', Search],
  ['/saved', 'Saved Jobs', Bookmark],
  ['/applications', 'Applied Jobs', FileCheck2],
  ['/profile', 'Profile', UserRound],
  ['/resume', 'Resume', FileText],
  ['/alerts', 'Job Alerts', Bell],
  ['/companies', 'Companies', Building2],
  ['/resources', 'Career Resources', BookOpen],
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <nav className="side-nav">
        {items.map(([to, label, Icon]) => (
          <NavLink key={label} to={to} className={({ isActive }) => `side-link ${isActive ? 'active' : ''}`}>
            <Icon size={19} strokeWidth={1.9} /> <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="profile-progress">
        <div className="rocket"><Rocket size={25} /></div>
        <h3>Get noticed faster</h3>
        <p>Complete your profile</p>
        <div className="progress-row"><div><span /></div><b>80%</b></div>
        <Link to="/profile" className="complete-button">Complete Profile <ArrowRight size={17} /></Link>
      </div>
    </aside>
  );
}
