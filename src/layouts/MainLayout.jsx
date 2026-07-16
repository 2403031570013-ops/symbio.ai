import { useEffect, useState } from 'react';
import { LayoutDashboard, PackagePlus, Sparkles, Repeat2, BarChart3, ShieldCheck, LogOut, Menu, Brain, Leaf, Truck, FileText, DollarSign, Bell, X } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import OnboardingAndPopups from '../components/OnboardingAndPopups';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/listings', label: 'Listings', icon: PackagePlus },
  { to: '/matches', label: 'AI Matches', icon: Sparkles },
  { to: '/transactions', label: 'Transactions', icon: Repeat2 },
  { to: '/esg', label: 'ESG', icon: BarChart3 },
  { to: '/ai-recommendations', label: 'AI Insights', icon: Brain },
  { to: '/esg-dashboard', label: 'ESG Dashboard', icon: Leaf },
  { to: '/supply-chain', label: 'Supply Chain', icon: Truck },
  { to: '/compliance', label: 'Compliance', icon: ShieldCheck },
  { to: '/marketplace', label: 'Marketplace', icon: DollarSign },
  { to: '/admin', label: 'Admin', icon: FileText },
];

export default function MainLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [notifications, setNotifications] = useState([]);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const [notificationsLoading, setNotificationsLoading] = useState(true);
  const visibleNavItems = navItems.filter((item) => item.to !== '/admin' || ['Admin', 'Super Admin'].includes(user?.role));
  const unreadCount = notifications.filter((item) => !item.read).length;

  const loadNotifications = async () => {
    try {
      const response = await api.get('/notifications');
      setNotifications(response.data?.data?.notifications || []);
    } catch {
      setNotifications([]);
    } finally {
      setNotificationsLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
    const intervalId = window.setInterval(loadNotifications, 15000);
    return () => window.clearInterval(intervalId);
  }, []);

  const requestPushPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  };

  const markRead = async (notification) => {
    try {
      await api.put(`/notifications/${notification.id}/read`);
      await loadNotifications();
    } catch {
      // Keep notification visible if marking read fails.
    }
  };

  const navLinkClass = ({ isActive }) =>
    `flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium transition duration-200 ${
      isActive ? 'bg-emerald-500/15 text-emerald-300 shadow-inner shadow-emerald-950/20' : 'text-slate-300 hover:bg-white/10 hover:text-white'
    }`;

  const navigation = (
    <nav className="space-y-1" aria-label="Primary navigation">
      {visibleNavItems.map(({ to, label, icon: Icon }) => (
        <NavLink key={to} to={to} onClick={() => setNavOpen(false)} className={navLinkClass}>
          <Icon size={18} aria-hidden="true" />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.15),_transparent_35%),linear-gradient(135deg,_#031427_0%,_#061b2c_55%,_#020812_100%)] text-slate-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 lg:flex-row lg:px-6 lg:py-6 pb-24 lg:pb-6">
        <aside className="hidden w-full rounded-3xl border border-white/10 bg-white/[0.07] p-4 shadow-2xl shadow-slate-950/30 backdrop-blur-xl lg:block lg:w-64 lg:p-5">
          <div className="mb-6">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-emerald-500/15 p-2 text-emerald-300">
                <Sparkles size={20} aria-hidden="true" />
              </div>
              <div>
                <p className="text-lg font-semibold text-white">SymbioAI</p>
                <p className="text-sm text-slate-400">Industrial symbiosis</p>
              </div>
            </div>
          </div>

          {navigation}

          <div className="mt-8 rounded-2xl border border-white/10 bg-slate-950/70 p-4">
            <p className="text-sm font-medium text-white">{user?.full_name || user?.name || user?.email || 'Signed in user'}</p>
            <p className="text-sm text-slate-400">{user?.role}</p>
            <button
              onClick={logout}
              className="mt-4 inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300"
            >
              <LogOut size={16} aria-hidden="true" />
              Sign out
            </button>
          </div>
        </aside>

        <main className="flex-1 space-y-6">
          <header className="flex items-center justify-between gap-3 rounded-3xl border border-white/10 bg-white/[0.07] px-4 py-4 shadow-xl shadow-slate-950/25 backdrop-blur-xl">
            <button
              type="button"
              onClick={() => setNavOpen(true)}
              className="rounded-full border border-white/10 bg-slate-950/70 p-3 text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300 lg:hidden"
              aria-label="Open navigation"
            >
              <Menu size={18} aria-hidden="true" />
            </button>
            <div>
              <p className="text-sm text-slate-400">Enterprise operations workspace</p>
              <h2 className="text-lg font-semibold text-white sm:text-xl">SymbioAI Command Center</h2>
            </div>
            <div className="relative flex items-center gap-2">
              <button type="button" onClick={() => { setNotificationsOpen((value) => !value); requestPushPermission(); }} className="relative rounded-full border border-white/10 bg-slate-950/80 p-3 text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300" aria-label="Open notifications" aria-expanded={notificationsOpen}>
                <Bell size={16} aria-hidden="true" />
                {unreadCount ? <span className="absolute -right-1 -top-1 rounded-full bg-emerald-400 px-1.5 py-0.5 text-xs font-black text-slate-950">{unreadCount}</span> : null}
              </button>
              <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-slate-950/80 px-3 py-2 text-sm text-slate-300 sm:flex">
                <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_16px_rgba(52,211,153,0.9)]" />
                Live network
              </div>
              {notificationsOpen ? (
                <div className="absolute right-0 top-14 z-40 w-[min(22rem,calc(100vw-2rem))] rounded-3xl border border-white/10 bg-slate-950/95 p-4 shadow-2xl shadow-slate-950/40 backdrop-blur-xl">
                  <div className="mb-3 flex items-center justify-between">
                    <h3 className="font-bold text-white">Notifications</h3>
                    <span className="text-xs text-emerald-300">{unreadCount} unread</span>
                  </div>
                  <div className="max-h-80 space-y-2 overflow-y-auto">
                    {notificationsLoading ? <p className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-400">Loading notifications...</p> : null}
                    {!notificationsLoading && notifications.length === 0 ? <p className="rounded-2xl border border-dashed border-slate-700 p-4 text-sm text-slate-400">No notifications yet. Critical match, order, and admin updates will appear here.</p> : null}
                    {notifications.map((item) => (
                      <button key={item.id} type="button" onClick={() => markRead(item)} className="w-full rounded-2xl border border-slate-800 bg-slate-900/80 p-3 text-left text-sm transition hover:border-emerald-400/40">
                        <p className="font-semibold text-white">{item.title || 'SymbioAI update'}</p>
                        <p className="mt-1 text-slate-400">{item.message}</p>
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </header>
          {location.state?.accessDenied ? (
            <div className="rounded-3xl border border-amber-300/30 bg-amber-400/10 p-4 text-sm font-semibold text-amber-100" role="alert">
              Access Denied. Admin portal access requires an Admin or Super Admin account.
            </div>
          ) : null}
          <Outlet />
        </main>
      </div>

      {navOpen ? (
        <div className="fixed inset-0 z-50 bg-slate-950/75 p-4 backdrop-blur-sm lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu">
          <div className="ml-auto flex h-full max-w-sm flex-col rounded-3xl border border-white/10 bg-slate-950/95 p-5 shadow-2xl">
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-emerald-500/15 p-2 text-emerald-300">
                  <Sparkles size={20} aria-hidden="true" />
                </div>
                <div>
                  <p className="font-semibold text-white">SymbioAI</p>
                  <p className="text-sm text-slate-400">{user?.role || 'Workspace'}</p>
                </div>
              </div>
              <button type="button" onClick={() => setNavOpen(false)} className="rounded-full border border-white/10 p-2 text-slate-300 hover:text-white" aria-label="Close navigation">
                <X size={18} aria-hidden="true" />
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto">{navigation}</div>
            <button onClick={logout} className="mt-5 inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-700 px-4 py-3 text-sm font-semibold text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300">
              <LogOut size={16} aria-hidden="true" />
              Sign out
            </button>
          </div>
        </div>
      ) : null}

      {/* Mobile Bottom Navigation Bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around border-t border-white/10 bg-slate-950/90 py-3.5 px-2 shadow-2xl backdrop-blur-xl lg:hidden" aria-label="Mobile navigation">
        {visibleNavItems.slice(0, 5).map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1.5 text-[10px] font-black transition duration-200 ${
                isActive ? 'text-emerald-400' : 'text-slate-400 hover:text-white'
              }`
            }
          >
            <Icon size={18} aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Global Onboarding & Popup Notification Center */}
      <OnboardingAndPopups />
    </div>
  );
}
