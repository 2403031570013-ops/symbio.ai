import { useEffect, useState } from 'react';
import { 
  Sparkles, CheckCircle2, ChevronRight, X, ArrowRight, ShieldCheck, 
  Trash2, Award, Trophy, Compass
} from 'lucide-react';

const steps = [
  {
    title: '🌍 Welcome to SymbioAI',
    description: 'Welcome to the future of industrial symbiosis. Let us show you how to trade industrial waste resources, reduce carbon emissions, and optimize your supply chain.',
    badge: 'Overview'
  },
  {
    title: '📊 Operations Dashboard',
    description: 'Your command center. Track total traded volume, pending listing validations, and circular carbon offsets. Get real-time system alerts on one clean board.',
    badge: 'Dashboard'
  },
  {
    title: '🛍 Industrial Marketplace',
    description: 'Directly buy and sell byproducts and raw materials with certified corporate partners. Secure escrow clearances ensure safe corporate payouts.',
    badge: 'Marketplace'
  },
  {
    title: '✨ AI Matchmaking',
    description: 'Our proprietary chemistry matcher scans regional catalogs to link producers and consumers based on chemical suitability, logistics cost, and ESG compliance.',
    badge: 'AI Engine'
  },
  {
    title: '📋 Material Listings',
    description: 'Publish your available waste or demand requirements. Upload certified lab reports and safety data sheets to get matched automatically.',
    badge: 'Listings'
  },
  {
    title: '🌱 Transactions & ESG',
    description: 'Track orders from transit to completion. Generate downloadable ESG impact statements and carbon diversion certificates for corporate reporting.',
    badge: 'ESG'
  },
  {
    title: '🔐 Administrative Controls',
    description: 'Admin operators can access the enterprise console to audit platform security trails, manage listings, and moderate messaging chats.',
    badge: 'Security'
  }
];

export default function OnboardingAndPopups() {
  const [showTour, setShowTour] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [popup, setPopup] = useState(null);

  useEffect(() => {
    // Check if user is logged in and hasn't seen the tour yet
    const hasSeenTour = localStorage.getItem('symbioai_tour_seen');
    if (!hasSeenTour) {
      setShowTour(true);
    }

    // Set up global listeners for dynamic popups / achievements
    const handleTriggerPopup = (e) => {
      setPopup(e.detail);
    };

    window.addEventListener('trigger-symbio-popup', handleTriggerPopup);
    return () => window.removeEventListener('trigger-symbio-popup', handleTriggerPopup);
  }, []);

  const closeTour = () => {
    localStorage.setItem('symbioai_tour_seen', 'true');
    setShowTour(false);
    
    // Trigger "Welcome Achievement" popup upon closing the onboarding tour
    triggerAchievement({
      title: '🌍 Onboarding Completed',
      message: 'Congratulations! You are now ready to operate the SymbioAI command center.',
      badge: 'Achievement Unlocked',
      type: 'achievement'
    });
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep((c) => c + 1);
    } else {
      closeTour();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep((c) => c - 1);
    }
  };

  const triggerAchievement = (detail) => {
    setPopup(detail);
  };

  if (!showTour && !popup) return null;

  return (
    <>
      {/* Onboarding Tour Modal */}
      {showTour && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-md">
          <div className="relative w-full max-w-lg rounded-3xl border border-white/10 bg-gradient-to-b from-slate-900 to-slate-950 p-6 md:p-8 shadow-2xl shadow-black/80 text-slate-100 overflow-hidden">
            {/* Ambient Background Glow */}
            <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-emerald-500/20 blur-3xl" />
            <div className="absolute -left-20 -bottom-20 h-40 w-40 rounded-full bg-cyan-500/10 blur-3xl" />

            <div className="relative space-y-6">
              <div className="flex items-center justify-between">
                <span className="rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 text-xs font-black text-emerald-400 uppercase tracking-widest">
                  {steps[currentStep].badge}
                </span>
                <button 
                  onClick={closeTour}
                  className="rounded-full border border-slate-800 p-1.5 text-slate-400 hover:text-white transition"
                  aria-label="Skip onboarding walkthrough"
                >
                  <X size={16} />
                </button>
              </div>

              <div className="space-y-3">
                <h3 className="text-2xl font-black text-white tracking-tight">{steps[currentStep].title}</h3>
                <p className="text-sm leading-relaxed text-slate-300">{steps[currentStep].description}</p>
              </div>

              {/* Progress Indicators */}
              <div className="flex gap-1.5 py-2">
                {steps.map((_, idx) => (
                  <div 
                    key={idx} 
                    className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                      idx === currentStep ? 'bg-gradient-to-r from-emerald-400 to-cyan-400' : 'bg-slate-800'
                    }`} 
                  />
                ))}
              </div>

              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={prevStep}
                  disabled={currentStep === 0}
                  className="px-4 py-2 text-xs font-bold text-slate-400 hover:text-white disabled:opacity-30 disabled:pointer-events-none transition"
                >
                  Back
                </button>
                <button
                  onClick={nextStep}
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 px-5 py-2.5 text-xs font-black text-slate-950 hover:opacity-90 shadow-lg shadow-emerald-950/20 transition duration-200"
                >
                  {currentStep === steps.length - 1 ? 'Finish' : 'Next Step'}
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Premium Achievement / Action Alert Popups */}
      {popup && (
        <div className="fixed bottom-6 right-6 z-[120] max-w-sm w-full p-4 rounded-3xl border border-emerald-400/20 bg-slate-900/90 shadow-2xl shadow-black/80 backdrop-blur-xl animate-in slide-in-from-bottom duration-300">
          <div className="flex items-start gap-4">
            <div className="rounded-2xl bg-emerald-500/10 p-2.5 text-emerald-400 border border-emerald-400/20">
              {popup.type === 'achievement' ? <Trophy size={20} /> : <Award size={20} />}
            </div>
            <div className="flex-1 space-y-1">
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">{popup.badge || 'System Notification'}</span>
              <h4 className="text-sm font-bold text-white leading-tight">{popup.title}</h4>
              <p className="text-xs text-slate-300 leading-relaxed">{popup.message}</p>
            </div>
            <button 
              onClick={() => setPopup(null)}
              className="text-slate-500 hover:text-white transition"
              aria-label="Close notification"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}

// Utility to dispatch popup alert from anywhere in the codebase
export function notifySymbio(detail) {
  const event = new CustomEvent('trigger-symbio-popup', { detail });
  window.dispatchEvent(event);
}
