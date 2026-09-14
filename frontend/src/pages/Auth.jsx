import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { BriefcaseBusiness, Eye, EyeOff, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Auth({ mode = 'login' }) {
  const isLogin = mode === 'login';
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [show, setShow] = useState(false); const [error, setError] = useState(''); const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault(); setError(''); setBusy(true);
    try { if (isLogin) await login(email, password); else await register(name, email, password); navigate(location.state?.from || '/'); }
    catch (err) { setError(err.response?.data?.message || 'Something went wrong. Please try again.'); }
    finally { setBusy(false); }
  };

  return <div className="auth-page"><div className="auth-card"><Link to="/" className="auth-brand"><span><BriefcaseBusiness size={24} /></span>JobHub</Link><h1>{isLogin ? 'Welcome back' : 'Create your JobHub account'}</h1><p>{isLogin ? 'Sign in to save jobs and track applications.' : 'Save jobs, track applications and get a faster job search.'}</p>
    <form onSubmit={submit}>{!isLogin && <label>Full name<input value={name} onChange={e => setName(e.target.value)} placeholder="Your name" required /></label>}<label>Email<input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required /></label><label>Password<div className="password-input"><input type={show ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 8 characters" required minLength={8} /><button type="button" onClick={() => setShow(!show)}>{show ? <EyeOff size={18}/> : <Eye size={18}/>}</button></div></label>{error && <div className="auth-error">{error}</div>}<button className="auth-submit" disabled={busy}>{busy ? 'Please wait...' : isLogin ? 'Sign in' : 'Create account'}</button></form>
    <div className="secure-note"><ShieldCheck size={17}/> JWT-secured account access</div><div className="auth-switch">{isLogin ? <>New to JobHub? <Link to="/register">Create an account</Link></> : <>Already have an account? <Link to="/login">Sign in</Link></>}</div>
  </div></div>;
}
