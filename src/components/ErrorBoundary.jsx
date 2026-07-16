import { Component } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('SymbioAI render failure', error, info);
  }

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.2),_transparent_35%),linear-gradient(135deg,_#031427_0%,_#061b2c_55%,_#020812_100%)] px-4 text-slate-100">
        <div className="max-w-lg rounded-3xl border border-white/10 bg-white/10 p-8 text-center shadow-2xl backdrop-blur-xl">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-500/15 text-rose-200">
            <AlertTriangle size={28} />
          </div>
          <h1 className="mt-5 text-2xl font-black text-white">Something needs a quick refresh</h1>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            The page hit an unexpected rendering issue. Your session is still protected, and a refresh usually restores the workspace.
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-emerald-700 px-5 py-3 font-bold text-white shadow-lg shadow-emerald-950/30 transition hover:scale-[1.01]"
          >
            <RefreshCcw size={18} />
            Refresh page
          </button>
        </div>
      </div>
    );
  }
}
