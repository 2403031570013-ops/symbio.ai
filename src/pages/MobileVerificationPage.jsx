import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Leaf, Smartphone, Phone } from 'lucide-react';
import api from '../services/api';
import { getApiError } from '../services/response';

export default function MobileVerificationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const [otpSent, setOtpSent] = useState(false);

  const userId = location.state?.userId || '';
  const email = location.state?.email || '';

  useEffect(() => {
    if (!cooldown) return undefined;
    const timer = window.setInterval(() => setCooldown((seconds) => Math.max(0, seconds - 1)), 1000);
    return () => window.clearInterval(timer);
  }, [cooldown]);

  const sendOtp = async () => {
    if (!phoneNumber || phoneNumber.replace(/\D/g, '').length < 10) {
      setError('Please enter a valid phone number');
      return;
    }

    setBusy(true);
    setError('');
    setMessage('');

    try {
      const response = await api.post('/auth/send-mobile-otp', {
        user_id: userId,
        phone_number: phoneNumber,
      });
      setMessage(response.data?.message || 'Verification code sent.');
      setCooldown(response.data?.data?.cooldown_seconds || 60);
      setOtpSent(true);
    } catch (requestError) {
      setError(getApiError(requestError, 'Unable to send verification code.'));
    } finally {
      setBusy(false);
    }
  };

  const verifyMobileOtp = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    setMessage('');

    try {
      const response = await api.post('/auth/verify-mobile', {
        user_id: userId,
        otp: otp,
      });
      setMessage(response.data?.message || 'Mobile verified successfully.');
      setTimeout(() => navigate('/dashboard'), 700);
    } catch (requestError) {
      setError(getApiError(requestError, 'Unable to verify code.'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.2),_transparent_35%),linear-gradient(135deg,_#031427_0%,_#061b2c_55%,_#020812_100%)] px-4 py-10">
      <form onSubmit={verifyMobileOtp} className="w-full max-w-md rounded-[2rem] border border-white/10 bg-white/10 p-8 shadow-2xl shadow-slate-950/30 backdrop-blur-xl">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-purple-400/15 text-purple-200">
          <Smartphone size={32} />
        </div>
        <h1 className="text-center text-3xl font-black text-white">Verify Mobile</h1>
        <p className="mt-2 text-center text-sm text-slate-300">Complete the final step by verifying your mobile number.</p>

        <div className="mt-6 space-y-4">
          <label className="block text-sm font-semibold text-slate-200">
            <span>Phone Number</span>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(event) => setPhoneNumber(event.target.value.replace(/\D/g, ''))}
              placeholder="+1 (555) 000-0000"
              disabled={otpSent}
              required
              className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-purple-400 disabled:opacity-50"
            />
          </label>

          <button
            type="button"
            disabled={busy || cooldown > 0 || !phoneNumber || otpSent}
            onClick={sendOtp}
            className="w-full rounded-2xl border border-purple-400/50 px-4 py-3 font-bold text-purple-200 transition hover:bg-purple-500/10 disabled:opacity-50"
          >
            <Phone className="mr-2 inline" size={18} />
            {cooldown ? `Resend available in ${cooldown}s` : 'Send verification code'}
          </button>

          {otpSent && (
            <label className="block text-sm font-semibold text-slate-200">
              <span>Six-digit OTP</span>
              <input
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                pattern="[0-9]{6}"
                value={otp}
                onChange={(event) => setOtp(event.target.value.replace(/\D/g, ''))}
                placeholder="000000"
                required
                className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-center text-2xl tracking-[0.45em] text-white outline-none transition focus:border-purple-400"
              />
            </label>
          )}
        </div>

        {error && <p className="mt-4 rounded-xl bg-rose-500/15 px-3 py-2 text-sm text-rose-200">{error}</p>}
        {message && <p className="mt-4 rounded-xl bg-purple-500/15 px-3 py-2 text-sm text-purple-100">{message}</p>}

        {otpSent && (
          <button
            type="submit"
            disabled={busy || otp.length !== 6}
            className="mt-5 w-full rounded-2xl bg-gradient-to-r from-purple-500 to-purple-700 px-4 py-3 font-black text-white shadow-lg shadow-purple-950/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {busy ? 'Verifying...' : 'Verify Mobile'}
          </button>
        )}

        <p className="mt-6 text-center text-xs text-slate-400">
          SymbioAI Registration • Step 3 of 3
        </p>
      </form>
    </div>
  );
}
