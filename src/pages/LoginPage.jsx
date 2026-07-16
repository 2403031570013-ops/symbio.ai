import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Globe2, Headphones, Leaf, Lock, Mail, Moon, Recycle, ShieldCheck, Sun, Wind } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../context/AuthContext';
import heroImage from '../assets/login-nature-hero.png';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [language, setLanguage] = useState('en');
  const [darkMode, setDarkMode] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, googleLoginWithCredential } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const rememberedEmail = localStorage.getItem('symbioai_remember_email');
    if (rememberedEmail) setEmail(rememberedEmail);
  }, []);

  const copy = language === 'hi'
    ? {
        welcome: 'Wapas swagat hai!',
        subtitle: 'Apne account me continue karne ke liye sign in karein',
        email: 'Email address',
        password: 'Password',
        remember: 'Mujhe yaad rakhein',
        forgot: 'Password bhool gaye?',
        signIn: 'Sign in',
        googleUnavailable: 'Google Sign-In ke liye VITE_GOOGLE_CLIENT_ID configure karein.',
        noAccount: 'Account nahi hai?',
        register: 'Abhi register karein',
        help: 'Madad chahiye?',
        helpText: 'English ya Hindi me step-by-step support paayein.',
        helpButton: 'Help Center kholein',
      }
    : {
        welcome: 'Welcome Back!',
        subtitle: 'Sign in to continue to your account',
        email: 'Email Address',
        password: 'Password',
        remember: 'Remember Me',
        forgot: 'Forgot Password?',
        signIn: 'Sign In',
        googleUnavailable: 'Configure VITE_GOOGLE_CLIENT_ID to enable Google Sign-In.',
        noAccount: "Don't have an account?",
        register: 'Register Now',
        help: 'Need Help?',
        helpText: 'Get step-by-step support in English or Hindi.',
        helpButton: 'Open Help Center',
      };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setNotice('');
    setIsSubmitting(true);

    try {
      await login(email, password, remember);
      if (remember) {
        localStorage.setItem('symbioai_remember_email', email);
      } else {
        localStorage.removeItem('symbioai_remember_email');
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Unable to sign in');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    if (!credentialResponse?.credential) {
      setError('Unable to sign in with Google. No credential received.');
      return;
    }
    setError('');
    setNotice('');
    setIsSubmitting(true);

    try {
      await googleLoginWithCredential(credentialResponse.credential);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Unable to sign in with Google');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`${darkMode ? 'bg-slate-950' : 'bg-emerald-50'} min-h-screen overflow-hidden text-slate-900`}>
      <div className="absolute right-4 top-4 z-20 flex items-center gap-3 sm:right-8 sm:top-8 sm:gap-4">
        <div className="rounded-full bg-white/75 px-4 py-2 text-sm font-semibold text-slate-700 shadow-lg backdrop-blur">
          <button type="button" onClick={() => setLanguage('en')} className={language === 'en' ? 'text-emerald-700' : ''}><Globe2 size={16} className="mr-1 inline" /> English</button>
          <span className="mx-2 text-slate-400">|</span>
          <button type="button" onClick={() => setLanguage('hi')} className={language === 'hi' ? 'text-emerald-700' : ''}>Hindi</button>
        </div>
        <button type="button" onClick={() => setDarkMode((value) => !value)} className="rounded-full bg-slate-900/80 p-2 text-white shadow-lg backdrop-blur" aria-label="Toggle theme">
          {darkMode ? <Sun size={22} /> : <Moon size={22} />}
        </button>
      </div>

      <div className="grid min-h-screen lg:grid-cols-[1.1fr_0.9fr]">
        <section className="relative flex min-h-[52vh] flex-col justify-between overflow-hidden p-8 pt-24 text-white lg:min-h-screen lg:p-12">
          <img src={heroImage} alt="Sustainable industrial valley" className="absolute inset-0 h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-950/25 via-slate-950/20 to-slate-950/70" />

          <div className="relative z-10 flex items-center gap-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/85 text-emerald-700 shadow-xl">
              <Leaf size={42} />
            </div>
            <div>
              <h1 className="text-4xl font-black tracking-tight">Symbio<span className="text-emerald-300">AI</span></h1>
              <p className="text-sm font-semibold text-emerald-50">Smart Connections. Sustainable Future.</p>
            </div>
          </div>

          <div className="relative z-10 max-w-2xl pb-8">
            <h2 className="text-5xl font-black leading-tight text-white drop-shadow-xl lg:text-7xl">Connecting Waste to Opportunity</h2>
            <p className="mt-6 text-2xl font-bold leading-relaxed text-white">AI-Powered Industrial Symbiosis Platform for a Greener Tomorrow</p>

            <div className="mt-8 grid max-w-2xl gap-3 rounded-3xl border border-white/20 bg-slate-950/35 p-4 shadow-2xl backdrop-blur md:grid-cols-3">
              <div className="flex items-center gap-3">
                <Leaf className="rounded-full bg-emerald-500/25 p-2 text-emerald-200" size={42} />
                <div><p className="text-sm text-emerald-50">Eco Impact</p><p className="font-bold">12,540+ Tons</p></div>
              </div>
              <div className="flex items-center gap-3 md:border-l md:border-white/20 md:pl-4">
                <Wind className="rounded-full bg-emerald-500/25 p-2 text-emerald-200" size={42} />
                <div><p className="text-sm text-emerald-50">Industries</p><p className="font-bold">1,250+</p></div>
              </div>
              <div className="flex items-center gap-3 md:border-l md:border-white/20 md:pl-4">
                <Recycle className="rounded-full bg-emerald-500/25 p-2 text-emerald-200" size={42} />
                <div><p className="text-sm text-emerald-50">Resources</p><p className="font-bold">8,320+</p></div>
              </div>
            </div>

            <p className="mt-8 text-lg font-medium text-white">"Sustainability is no longer about doing less harm. It is about <span className="text-emerald-300">creating more good</span>."</p>
          </div>
        </section>

        <section className="relative flex items-center justify-center p-6 lg:p-12">
          <div className="absolute inset-0 bg-gradient-to-br from-white via-emerald-50 to-cyan-50" />
          <div className="relative z-10 w-full max-w-xl space-y-6">
            <div className="rounded-[2rem] border border-white/70 bg-white/72 p-8 shadow-2xl backdrop-blur-xl lg:p-10">
              <div className="mx-auto mb-6 flex h-28 w-28 items-center justify-center rounded-full bg-emerald-50 text-emerald-700 shadow-inner">
                <Leaf size={58} />
              </div>
              <h2 className="text-center text-4xl font-black text-slate-900">Symbio<span className="text-emerald-600">AI</span></h2>
              <h3 className="mt-5 text-center text-2xl font-black text-slate-800">{copy.welcome}</h3>
              <p className="mt-2 text-center text-slate-600">{copy.subtitle}</p>

              <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
                <label className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-sm focus-within:border-emerald-400">
                  <Mail size={22} className="text-slate-500" />
                  <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="w-full bg-transparent text-slate-900 outline-none" placeholder={copy.email} required />
                </label>
                <label className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-sm focus-within:border-emerald-400">
                  <Lock size={22} className="text-slate-500" />
                  <input type={showPassword ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} className="w-full bg-transparent text-slate-900 outline-none" placeholder={copy.password} required />
                  <button type="button" onClick={() => setShowPassword((value) => !value)} className="text-slate-500" aria-label="Toggle password visibility">
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </label>

                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center gap-2 font-medium text-slate-700">
                    <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} className="h-4 w-4 accent-emerald-600" />
                    {copy.remember}
                  </label>
                  <Link to="/forgot-password" className="font-semibold text-emerald-700 hover:text-emerald-800">{copy.forgot}</Link>
                </div>

                {error ? <p className="rounded-2xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p> : null}
                {notice ? <p className="rounded-2xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{notice}</p> : null}

                <button type="submit" disabled={isSubmitting} className="flex w-full items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-emerald-800 px-5 py-4 text-lg font-black text-white shadow-lg shadow-emerald-900/20 transition hover:scale-[1.01] disabled:opacity-70">
                  {isSubmitting ? 'Signing in...' : copy.signIn}
                </button>
              </form>

              <div className="my-6 flex items-center gap-4 text-sm text-slate-500">
                <div className="h-px flex-1 bg-slate-200" />
                or continue with
                <div className="h-px flex-1 bg-slate-200" />
              </div>

              <div className="flex w-full items-center justify-center">
                {googleClientId ? (
                  <div className="w-full max-w-sm">
                    <GoogleLogin onSuccess={handleGoogleSuccess} onError={() => setError('Unable to sign in with Google')} theme="outline" shape="pill" text="continue_with" width="360" />
                  </div>
                ) : (
                  <p className="w-full rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-center text-sm font-semibold text-amber-800">
                    {copy.googleUnavailable}
                  </p>
                )}
              </div>

              <p className="mt-7 text-center text-slate-600">
                {copy.noAccount} <Link to="/register" className="font-black text-emerald-700 hover:text-emerald-800">{copy.register}</Link>
              </p>
            </div>

            <div className="rounded-[1.5rem] border border-white/70 bg-white/80 p-5 shadow-xl backdrop-blur-xl">
              <div className="flex items-center gap-4">
                <div className="rounded-full bg-emerald-100 p-4 text-emerald-700"><Headphones size={28} /></div>
                <div className="flex-1">
                  <h4 className="font-black text-slate-800">{copy.help}</h4>
                  <p className="text-sm text-slate-600">{copy.helpText}</p>
                  <button type="button" onClick={() => document.querySelector('[aria-label="Open help center"]')?.click()} className="mt-2 rounded-full border border-emerald-300 px-4 py-1.5 text-sm font-bold text-emerald-700 hover:bg-emerald-50">{copy.helpButton}</button>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-4 text-sm font-semibold text-slate-600">
              <span>Copyright 2026 SymbioAI</span>
              <span className="inline-flex items-center gap-1"><Lock size={15} /> Privacy Policy</span>
              <span className="inline-flex items-center gap-1"><ShieldCheck size={15} /> Terms & Conditions</span>
              <span>v1.0.0</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
