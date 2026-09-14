import { Link, useNavigate } from 'react-router-dom';
import { Bell, ChevronDown, Search, BriefcaseBusiness, MapPin } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function Navbar({ onSearch, onLocation }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [locationOpen, setLocationOpen] = useState(false);
  const [locations, setLocations] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const locationRef = useRef(null);

  useEffect(() => {
    api.getLocations().then(({ data }) => setLocations(data.countries || [])).catch(() => setLocations([]));
  }, []);

  useEffect(() => {
    const close = (event) => {
      if (locationRef.current && !locationRef.current.contains(event.target)) setLocationOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  const submit = (e) => {
    e.preventDefault();
    onSearch?.(query);
  };

  const chooseCountry = (country) => {
    setSelectedCountry(country);
    setSelectedLocation('');
    onLocation?.({ country, location: '' });
  };

  const chooseLocation = (location) => {
    setSelectedLocation(location);
    onLocation?.({ country: selectedCountry, location });
    setLocationOpen(false);
  };

  const clearLocation = () => {
    setSelectedCountry('');
    setSelectedLocation('');
    onLocation?.({ country: '', location: '' });
    setLocationOpen(false);
  };

  const countryData = locations.find((item) => item.name === selectedCountry);
  const label = selectedLocation || selectedCountry || 'Location';

  return (
    <header className="topbar">
      <Link className="brand" to="/">
        <span className="brand-icon"><BriefcaseBusiness size={24} strokeWidth={2.3} /></span>
        <span><strong>JobHub</strong><small>All Jobs. One Place.</small></span>
      </Link>

      <form className="top-search" onSubmit={submit}>
        <Search size={19} />
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search jobs, companies, or skills..." />

        <div className="location-picker" ref={locationRef}>
          <button type="button" className="top-location" onClick={() => setLocationOpen((v) => !v)}>
            <MapPin size={16} />
            <span title={label}>{label}</span>
            <ChevronDown size={15} />
          </button>

          {locationOpen && (
            <div className="location-menu">
              <div className="location-menu-head">
                <div><b>Job locations</b><small>Choose a country, then an available location</small></div>
                {(selectedCountry || selectedLocation) && <button type="button" onClick={clearLocation}>Clear</button>}
              </div>

              {!selectedCountry ? (
                <div className="location-list">
                  {locations.length === 0 ? (
                    <div className="location-empty">No job locations available yet.</div>
                  ) : locations.map((item) => (
                    <button type="button" className="location-option country-option" key={item.name} onClick={() => chooseCountry(item.name)}>
                      <span>{item.name}</span><small>{item.locations.length} locations</small><ChevronDown size={15} />
                    </button>
                  ))}
                </div>
              ) : (
                <div className="location-list">
                  <button type="button" className="location-back" onClick={() => setSelectedCountry('')}>← All countries</button>
                  <div className="selected-country">{selectedCountry}</div>
                  {countryData?.locations?.map((location) => (
                    <button type="button" className="location-option" key={location} onClick={() => chooseLocation(location)}>
                      <MapPin size={15} /><span>{location}</span>
                    </button>
                  ))}
                  {!countryData?.locations?.length && <div className="location-empty">No specific locations available.</div>}
                </div>
              )}
            </div>
          )}
        </div>

        <button type="submit">Search</button>
      </form>

      <div className="top-actions">
        <button className="icon-button notification"><Bell size={22} /><i /></button>
        <div className="profile-wrap">
          <button className="profile-button" onClick={() => setOpen((v) => !v)}>
            <span className="avatar">{user?.name?.[0]?.toUpperCase() || 'G'}</span>
            <span className="hello">Hi, {user?.name?.split(' ')[0] || 'Guest'}</span>
            <ChevronDown size={16} />
          </button>
          {open && (
            <div className="profile-menu">
              {user?.role === 'admin' && <button onClick={() => { setOpen(false); navigate('/admin'); }}>Admin Dashboard</button>}{user ? <button onClick={() => { logout(); setOpen(false); navigate('/'); }}>Log out</button> : <Link to="/login" onClick={() => setOpen(false)}>Sign in</Link>}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
