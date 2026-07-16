import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Leaf, Building2 } from 'lucide-react';
import api from '../services/api';
import { getApiError } from '../services/response';

export default function FactoryVerificationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [factoryCode, setFactoryCode] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  
  const email = location.state?.email || '';
  const userId = location.state?.userId || '';

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    setMessage('');

    try {
      await api.post('/auth/verify-factory', { factory_code: factoryCode });
      setMessage('Factory verified successfully!');
      setTimeout(() => {
        navigate('/verify-email', { state: { email, userId } });
      }, 700);
    } catch (requestError) {
      setError(getApiError(requestError, 'Unable to verify factory code.'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.2),_transparent_35%),linear-gradient(135deg,_#031427_0%,_#061b2c_55%,_#020812_100%)] px-4 py-10">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-[2rem] border border-white/10 bg-white/10 p-8 shadow-2xl shadow-slate-950/30 backdrop-blur-xl">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-400/15 text-blue-200">
          <Building2 size={32} />
        </div>
        <h1 className="text-center text-3xl font-black text-white">Verify Factory</h1>
        <p className="mt-2 text-center text-sm text-slate-300">Enter your factory verification code to continue registration.</p>

        <label className="mt-6 block text-sm font-semibold text-slate-200">
          <span>Factory Code</span>
          <input
            type="text"
            value={factoryCode}
            onChange={(event) => setFactoryCode(event.target.value)}
            placeholder="Enter your factory code"
            required
            className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-blue-400"
          />
        </label>
        
        <p className="mt-3 text-xs text-slate-400">
          📌 Temporary code for setup: <strong>654321</strong>
        </p>

        {error && <p className="mt-4 rounded-2xl border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">{error}</p>}
        {message && <p className="mt-4 rounded-2xl border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200">{message}</p>}
        
        <button
          type="submit"
          disabled={busy || !factoryCode}
          className="mt-5 w-full rounded-2xl bg-gradient-to-r from-blue-500 to-blue-700 px-4 py-3 font-black text-white shadow-lg shadow-blue-950/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {busy ? 'Verifying...' : 'Verify Factory'}
        </button>

        <p className="mt-6 text-center text-xs text-slate-400">
          SymbioAI Registration • Step 1 of 3
        </p>
      </form>
    </div>
  );
}
