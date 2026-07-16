import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { getApiError } from '../services/response';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Waste Producer');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await register(name, email, password, role);
      const userId = response?.user_id || '';
      navigate('/verify-factory', { state: { email, userId } });
    } catch (err) {
      setError(err.message || 'Unable to create account');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.2),_transparent_35%),linear-gradient(135deg,_#031427_0%,_#061b2c_55%,_#020812_100%)] px-4 py-10">
      <div className="w-full max-w-md rounded-[2rem] border border-white/10 bg-white/10 p-8 shadow-2xl shadow-slate-950/30 backdrop-blur-xl">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-400/15 text-emerald-200">
          <Leaf size={32} />
        </div>
        <h1 className="text-center text-3xl font-black text-white">Create account</h1>
        <p className="mt-2 text-center text-sm text-slate-300">Join the SymbioAI ecosystem and unlock industrial matching.</p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm font-semibold text-slate-200">
            <span>Full name</span>
            <input value={name} onChange={(event) => setName(event.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-emerald-400" placeholder="Ava Chen" required />
          </label>
          <label className="block text-sm font-semibold text-slate-200">
            <span>Email</span>
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-emerald-400" placeholder="you@company.com" required />
          </label>
          <label className="block text-sm font-semibold text-slate-200">
            <span>Password</span>
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-emerald-400" placeholder="Create a strong password" required minLength={8} />
          </label>
          <label className="block text-sm font-semibold text-slate-200">
            <span>Role</span>
            <select value={role} onChange={(event) => setRole(event.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-emerald-400">
              <option value="Waste Producer">Waste Producer</option>
              <option value="Raw Material Consumer">Raw Material Consumer</option>
            </select>
            <span className="mt-2 block text-xs font-normal text-slate-400">Admin access is provisioned separately for security.</span>
          </label>
          {error ? <p className="rounded-2xl border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">{error}</p> : null}
          <button type="submit" disabled={isSubmitting} className="w-full rounded-2xl bg-gradient-to-r from-emerald-500 to-emerald-700 px-4 py-3 font-black text-white shadow-lg shadow-emerald-950/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70">
            {isSubmitting ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-300">
          Already registered? <Link to="/login" className="font-bold text-emerald-200">Sign in</Link>
        </p>
        
        <p className="mt-4 text-center text-xs text-slate-400">
          Registration is now a 3-step process: Factory → Email → Mobile verification
        </p>
      </div>
    </div>
  );
}
