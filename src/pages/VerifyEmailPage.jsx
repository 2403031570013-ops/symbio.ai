import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Leaf, MailCheck } from 'lucide-react';
import api from '../services/api';
import { getApiError } from '../services/response';

export default function VerifyEmailPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState(location.state?.email || '');
  const [otp, setOtp] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  
  const userId = location.state?.userId || '';

  useEffect(() => {
    if (!cooldown) return undefined;
    const timer = window.setInterval(() => setCooldown((seconds) => Math.max(0, seconds - 1)), 1000);
    return () => window.clearInterval(timer);
  }, [cooldown]);

  const sendOtp = async () => {
    setBusy(true); setError(''); setMessage('');
    try {
      const response = await api.post('/auth/send-otp', { email });
      setMessage(response.data?.message || 'Verification code sent.');
      setCooldown(response.data?.data?.cooldown_seconds || 60);
    } catch (requestError) {
      setError(getApiError(requestError, 'Unable to send verification code.'));
    } finally { setBusy(false); }
  };

  const verifyOtp = async (event) => {
    event.preventDefault();
    setBusy(true); setError(''); setMessage('');
    try {
      const response = await api.post('/auth/verify-otp', { email, otp });
      setMessage(response.data?.message || 'Email verified successfully.');
      window.setTimeout(() => navigate('/verify-mobile', { state: { userId, email } }), 700);
    } catch (requestError) {
      setError(getApiError(requestError, 'Unable to verify code.'));
    } finally { setBusy(false); }
  };

  return <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
    <form onSubmit={verifyOtp} className="w-full max-w-md rounded-3xl border border-white/10 bg-white/[0.07] p-8 text-white shadow-2xl backdrop-blur">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-400/15 text-emerald-300"><Leaf size={32} /></div>
      <h1 className="mt-5 text-center text-3xl font-black">Verify your email</h1>
      <p className="mt-2 text-center text-sm text-slate-300">We will send a six-digit code using Resend. It expires after five minutes.</p>
      <label className="mt-6 block text-sm font-semibold text-slate-200">Email
        <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none focus:border-emerald-400" />
      </label>
      <button type="button" disabled={busy || cooldown > 0 || !email} onClick={sendOtp} className="mt-3 w-full rounded-2xl border border-emerald-400/50 px-4 py-3 font-bold text-emerald-200 disabled:opacity-50">
        <MailCheck className="mr-2 inline" size={18} />{cooldown ? `Resend available in ${cooldown}s` : 'Send verification code'}
      </button>
      <label className="mt-5 block text-sm font-semibold text-slate-200">Six-digit OTP
        <input inputMode="numeric" autoComplete="one-time-code" maxLength={6} pattern="[0-9]{6}" value={otp} onChange={(event) => setOtp(event.target.value.replace(/\D/g, ''))} required className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-center text-2xl tracking-[0.45em] text-white outline-none focus:border-emerald-400" />
      </label>
      {error && <p className="mt-4 rounded-xl bg-rose-500/15 px-3 py-2 text-sm text-rose-200">{error}</p>}
      {message && <p className="mt-4 rounded-xl bg-emerald-500/15 px-3 py-2 text-sm text-emerald-100">{message}</p>}
      <button disabled={busy || otp.length !== 6} className="mt-5 w-full rounded-2xl bg-emerald-600 px-4 py-3 font-black text-white disabled:opacity-50">{busy ? 'Please wait...' : 'Verify email'}</button>
      <p className="mt-5 text-center text-xs text-slate-400">
        SymbioAI Registration • Step 2 of 3
      </p>
      <p className="mt-2 text-center text-sm text-slate-300"><Link to="/login" className="font-bold text-emerald-300">Return to sign in</Link></p>
    </form>
  </div>;
}
