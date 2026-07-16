import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Database, LockKeyhole, ShieldCheck, Terminal, UserCog } from 'lucide-react';
import api from '../services/api';
import { getApiError } from '../services/response';

export default function AdminLoginPage() {
  const [email, setEmail] = useState('admin@symbioai.com');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const response = await api.post('/auth/admin-login', { email, password });
      const token = response.data?.data?.token;
      if (!token) throw new Error('Missing admin session token');
      localStorage.setItem('symbioai_token', token);
      navigate('/admin', { replace: true });
      window.location.reload();
    } catch (err) {
      setError(getApiError(err, 'Admin sign-in failed'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen overflow-hidden bg-[#05070d] text-slate-100">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_10%,rgba(16,185,129,0.22),transparent_32%),radial-gradient(circle_at_80%_20%,rgba(59,130,246,0.16),transparent_30%),linear-gradient(135deg,#05070d_0%,#07111f_55%,#020409_100%)]" />
      <main className="relative z-10 grid min-h-screen lg:grid-cols-[1fr_0.82fr]">
        <section className="flex flex-col justify-between p-8 lg:p-12">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl border border-emerald-300/30 bg-emerald-400/10 p-3 text-emerald-200 shadow-lg shadow-emerald-950/30">
              <ShieldCheck size={30} />
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">SymbioAI</p>
              <h1 className="text-2xl font-black text-white">Enterprise Control Plane</h1>
            </div>
          </div>

          <div className="max-w-3xl py-16">
            <p className="inline-flex rounded-full border border-emerald-300/20 bg-emerald-400/10 px-4 py-2 text-sm font-semibold text-emerald-200">Admin-only secure access</p>
            <h2 className="mt-8 text-4xl font-black tracking-tight text-white sm:text-6xl">Operations, trust, revenue, and platform security in one command center.</h2>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">Use this portal to moderate the marketplace, manage users and companies, monitor AI matches, review audit logs, and verify system health.</p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {[
              ['RBAC', 'JWT verified admin APIs', LockKeyhole],
              ['Health', 'API and database status', Activity],
              ['Audit', 'Every action timestamped', Database],
            ].map(([title, text, Icon]) => (
              <div key={title} className="rounded-3xl border border-white/10 bg-white/[0.06] p-5 shadow-xl shadow-slate-950/30 backdrop-blur-xl">
                <Icon className="text-emerald-300" size={24} />
                <p className="mt-4 font-bold text-white">{title}</p>
                <p className="mt-1 text-sm text-slate-400">{text}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="flex items-center justify-center p-6 lg:p-12">
          <div className="w-full max-w-md rounded-[2rem] border border-white/10 bg-white/[0.08] p-8 shadow-2xl shadow-black/40 backdrop-blur-2xl">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-950 text-emerald-300 shadow-inner">
              <UserCog size={34} />
            </div>
            <h2 className="mt-6 text-center text-3xl font-black text-white">Admin Login</h2>
            <p className="mt-2 text-center text-sm text-slate-400">Separate privileged access for Admin and Super Admin accounts.</p>

            <form className="mt-8 space-y-4" onSubmit={submit}>
              <label className="block text-sm font-semibold text-slate-200">
                Admin email
                <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition focus:border-emerald-400" required />
              </label>
              <label className="block text-sm font-semibold text-slate-200">
                Password
                <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition focus:border-emerald-400" placeholder="Admin password" required />
              </label>

              {error ? <div className="rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}

              <button type="submit" disabled={submitting} className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-400 to-cyan-400 px-5 py-3 font-black text-slate-950 shadow-lg shadow-emerald-950/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70">
                <Terminal size={18} />
                {submitting ? 'Verifying admin session...' : 'Enter Admin Portal'}
              </button>
            </form>

            <div className="mt-6 rounded-2xl border border-slate-700/70 bg-slate-950/70 p-4 text-xs leading-6 text-slate-400">
              <p><span className="font-bold text-slate-200">Super Admin:</span> admin@symbioai.com / Admin@123</p>
              <p><span className="font-bold text-slate-200">Admin:</span> manager@symbioai.com / Manager@123</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
