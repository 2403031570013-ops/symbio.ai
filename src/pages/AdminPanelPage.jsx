import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity, AlertTriangle, BarChart3, Bell, Bot, CheckCircle2, ClipboardList, Database, Download,
  Factory, FileSpreadsheet, HeartPulse, LockKeyhole, Megaphone, MessageSquareWarning, RefreshCw,
  Search, Settings, ShieldCheck, ShoppingBag, SlidersHorizontal, Trash2, UserCog, Users, XCircle,
  FileText, LogOut, ArrowLeft, Plus, Edit2, ShieldAlert
} from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { getApiError, unwrapData } from '../services/response';

const sections = [
  ['dashboard', 'Dashboard', BarChart3],
  ['users', 'Users', Users],
  ['companies', 'Companies', Factory],
  ['listings', 'Listings', ClipboardList],
  ['marketplace', 'Marketplace', ShoppingBag],
  ['transactions', 'Transactions', FileSpreadsheet],
  ['ai', 'AI Engine', Bot],
  ['chat', 'Chat Moderation', MessageSquareWarning],
  ['reports', 'Reports', Download],
  ['analytics', 'Analytics', Activity],
  ['health', 'System Health', HeartPulse],
  ['logs', 'Audit Logs', LockKeyhole],
  ['notifications', 'Notifications', Bell],
  ['settings', 'Settings', Settings],
];

const roleOptions = ['Super Admin', 'Admin', 'Waste Producer', 'Raw Material Consumer'];
const listingStatuses = ['pending', 'approved', 'rejected', 'archived', 'flagged'];
const txStatuses = ['Pending', 'In Transit', 'Completed', 'Refunded', 'Disputed', 'Cancelled'];

function ShellCard({ children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-slate-800 bg-[#0d1527]/90 p-6 shadow-xl shadow-black/40 backdrop-blur-xl transition hover:border-slate-700/50 ${className}`}>
      {children}
    </div>
  );
}

function Kpi({ title, value, caption, icon: Icon, tone = 'emerald' }) {
  const tones = {
    emerald: 'text-emerald-400 bg-emerald-400/10 border border-emerald-400/20',
    cyan: 'text-cyan-400 bg-cyan-400/10 border border-cyan-400/20',
    amber: 'text-amber-400 bg-amber-400/10 border border-amber-400/20',
    rose: 'text-rose-400 bg-rose-400/10 border border-rose-400/20',
    purple: 'text-purple-400 bg-purple-400/10 border border-purple-400/20'
  };
  return (
    <ShellCard>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{title}</p>
          <p className="mt-3 text-3xl font-black tracking-tight text-white">{value}</p>
          <p className="mt-2 text-xs text-slate-400">{caption}</p>
        </div>
        <div className={`rounded-2xl p-3 ${tones[tone] || tones.emerald}`}>
          <Icon size={22} />
        </div>
      </div>
    </ShellCard>
  );
}

function ActionButton({ children, onClick, tone = 'neutral', disabled = false, type = 'button' }) {
  const tones = {
    neutral: 'border-slate-700 bg-slate-800/40 text-slate-200 hover:border-cyan-400/60 hover:text-white',
    approve: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/25 hover:border-emerald-500/50',
    danger: 'border-rose-500/30 bg-rose-500/10 text-rose-300 hover:bg-rose-500/25 hover:border-rose-500/50',
    warn: 'border-amber-500/30 bg-amber-500/10 text-amber-300 hover:bg-amber-500/25 hover:border-amber-500/50',
    primary: 'border-emerald-400 bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 hover:opacity-90 font-black'
  };
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`inline-flex items-center justify-center gap-2 rounded-xl border px-3 py-2 text-xs font-bold transition duration-200 disabled:cursor-not-allowed disabled:opacity-40 ${tones[tone]}`}
    >
      {children}
    </button>
  );
}

export default function AdminPanelPage() {
  const { user: authUser, logout } = useAuth();
  const navigate = useNavigate();

  const [active, setActive] = useState('dashboard');
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [query, setQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [listingFilter, setListingFilter] = useState('');
  const [selectedListings, setSelectedListings] = useState([]);
  const [broadcast, setBroadcast] = useState({ title: '', message: '' });
  const [threshold, setThreshold] = useState(80);

  // Edit Modals State
  const [editingUser, setEditingUser] = useState(null);
  const [editingListing, setEditingListing] = useState(null);
  const [selectedFactoryDocs, setSelectedFactoryDocs] = useState(null);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const stats = data.dashboard?.stats || {};
  const users = data.users || [];
  const listings = data.listings || [];
  const factories = data.factories || [];
  const transactions = data.transactions || [];
  const matches = data.matches || [];
  const chat = data.chat || { conversations: [], messages: [] };
  const health = data.health || {};
  const logs = data.logs || {};

  const visibleUsers = useMemo(() => users.filter((user) => {
    const haystack = `${user.full_name} ${user.email}`.toLowerCase();
    return haystack.includes(query.toLowerCase()) && (!roleFilter || user.role === roleFilter);
  }), [users, query, roleFilter]);

  const visibleListings = useMemo(() => listings.filter((item) => {
    const matchesQuery = item.name.toLowerCase().includes(query.toLowerCase()) || 
                         item.chemical_composition.toLowerCase().includes(query.toLowerCase());
    return matchesQuery && (!listingFilter || item.status === listingFilter);
  }), [listings, query, listingFilter]);

  const loadAdmin = async () => {
    setLoading(true);
    setError('');
    try {
      const [dashboardRes, usersRes, factoriesRes, listingsRes, transactionsRes, matchesRes, healthRes, logsRes, chatRes, settingsRes] = await Promise.all([
        api.get('/admin/dashboard'),
        api.get('/admin/users'),
        api.get('/admin/factories'),
        api.get('/admin/listings'),
        api.get('/admin/transactions'),
        api.get('/admin/ai-matches'),
        api.get('/admin/system-health'),
        api.get('/admin/logs'),
        api.get('/admin/chat'),
        api.get('/admin/settings'),
      ]);
      const ai = unwrapData(matchesRes) || {};
      setThreshold(ai.threshold || 80);
      setData({
        dashboard: unwrapData(dashboardRes),
        users: unwrapData(usersRes)?.users || [],
        factories: unwrapData(factoriesRes)?.factories || [],
        listings: unwrapData(listingsRes)?.listings || [],
        transactions: unwrapData(transactionsRes)?.transactions || [],
        matches: ai.matches || [],
        health: unwrapData(healthRes),
        logs: unwrapData(logsRes),
        chat: unwrapData(chatRes),
        settings: unwrapData(settingsRes)?.settings || {},
      });
    } catch (err) {
      setError(getApiError(err, 'Unable to load admin portal'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdmin();
  }, []);

  const runAction = async (success, action) => {
    setError('');
    setNotice('');
    try {
      await action();
      setNotice(success);
      await loadAdmin();
    } catch (err) {
      setError(getApiError(err, 'Admin action failed'));
    }
  };

  const downloadExport = async (resource, fmt = 'csv') => {
    try {
      const response = await api.get(`/admin/export/${resource}.${fmt}`, { responseType: 'blob' });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${resource}.${fmt}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(getApiError(err, 'Unable to export report'));
    }
  };

  const bulkStatus = (status) => runAction(`Bulk ${status} completed`, () => api.post('/admin/listings/bulk-status', { ids: selectedListings, status }));

  const handleEditUser = async (e) => {
    e.preventDefault();
    if (!editingUser) return;
    runAction('User details updated successfully', () => 
      api.put(`/admin/users/${editingUser.id}`, {
        full_name: editingUser.full_name,
        email_verified: editingUser.email_verified,
        factory_logo_url: editingUser.factory_logo_url
      })
    );
    setEditingUser(null);
  };

  const handleEditListing = async (e) => {
    e.preventDefault();
    if (!editingListing) return;
    runAction('Listing updated successfully', () =>
      api.put(`/admin/listings/${editingListing.id}`, {
        name: editingListing.name,
        chemical_composition: editingListing.chemical_composition,
        physical_state: editingListing.physical_state,
        quantity: editingListing.quantity,
        frequency: editingListing.frequency,
        certificate: editingListing.certificate
      })
    );
    setEditingListing(null);
  };

  const fetchFactoryDocs = async (factoryId) => {
    setLoadingDocs(true);
    setSelectedFactoryDocs(null);
    try {
      const res = await api.get(`/admin/factories/${factoryId}/documents`);
      setSelectedFactoryDocs(unwrapData(res)?.documents || []);
    } catch (err) {
      setError(getApiError(err, 'Unable to fetch factory documents'));
    } finally {
      setLoadingDocs(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#040814] text-slate-100 font-sans antialiased">
      {/* Background Neon Gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_15%,rgba(16,185,129,0.18),transparent_40%),radial-gradient(circle_at_70%_80%,rgba(6,182,212,0.15),transparent_40%)] pointer-events-none" />

      <div className="grid lg:grid-cols-[18rem_1fr] min-h-screen">
        {/* Left Enterprise Sidebar */}
        <aside className="relative z-10 border-r border-slate-800 bg-[#080e1c] flex flex-col justify-between p-6">
          <div>
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-gradient-to-br from-emerald-400 to-cyan-500 p-2.5 text-slate-950 shadow-lg shadow-emerald-500/10">
                <ShieldCheck size={26} className="animate-pulse" />
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.25em] font-black text-emerald-400">SymbioAI</p>
                <h1 className="text-lg font-black tracking-tight text-white">Enterprise Admin</h1>
              </div>
            </div>

            <nav className="mt-8 space-y-1.5" aria-label="Admin Navigation">
              {sections.map(([id, label, Icon]) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => { setActive(id); setQuery(''); setError(''); setNotice(''); }}
                  className={`w-full flex items-center gap-3.5 rounded-xl px-4 py-3 text-left text-sm font-semibold transition-all duration-200 ${
                    active === id 
                      ? 'bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/30 text-emerald-300 shadow-[0_0_20px_rgba(52,211,153,0.05)]' 
                      : 'text-slate-400 border border-transparent hover:bg-slate-800/40 hover:text-white'
                  }`}
                >
                  <Icon size={18} className={active === id ? 'text-emerald-400' : 'text-slate-400'} /> 
                  <span>{label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Admin User Card / Footer */}
          <div className="mt-8 pt-6 border-t border-slate-800 space-y-4">
            <div className="rounded-2xl bg-slate-900/60 p-4 border border-slate-800/80">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Active Operator</p>
              <p className="mt-1 text-sm font-bold text-white truncate">{authUser?.full_name || authUser?.email}</p>
              <span className="mt-1 inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400 border border-emerald-400/20">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping" />
                {authUser?.role}
              </span>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800/30 py-2.5 text-xs font-bold text-slate-300 transition hover:bg-slate-800 hover:text-white"
              >
                <ArrowLeft size={14} /> Back
              </button>
              <button
                type="button"
                onClick={logout}
                className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-rose-500/20 bg-rose-500/10 py-2.5 text-xs font-bold text-rose-400 transition hover:bg-rose-500/20 hover:text-rose-300"
              >
                <LogOut size={14} /> Out
              </button>
            </div>
          </div>
        </aside>

        {/* Main Work Area */}
        <main className="relative z-10 p-6 sm:p-8 space-y-6 overflow-y-auto max-h-screen">
          {/* Header */}
          <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-slate-800/60 pb-6">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.3em] text-emerald-400">Control Center</p>
              <h2 className="mt-1 text-3xl font-black tracking-tight text-white capitalize">{active} Panel</h2>
              <p className="text-sm text-slate-400 mt-1">Real-time administration, platform security controls, and enterprise operations monitoring.</p>
            </div>
            <div className="flex gap-2 self-start md:self-auto">
              <ActionButton onClick={loadAdmin} tone="neutral">
                <RefreshCw size={15} /> Sync State
              </ActionButton>
            </div>
          </header>

          {/* Messages */}
          {error && (
            <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300 flex items-center gap-3">
              <ShieldAlert size={18} />
              <span>{error}</span>
            </div>
          )}
          {notice && (
            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300 flex items-center gap-3">
              <CheckCircle2 size={18} />
              <span>{notice}</span>
            </div>
          )}

          {loading ? (
            <div className="flex justify-center items-center py-20">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-800 border-t-emerald-400" />
            </div>
          ) : (
            <>
              {/* Dashboard Section */}
              {active === 'dashboard' && (
                <div className="space-y-8">
                  {/* KPIs */}
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <Kpi title="Total Users" value={stats.total_users || 0} caption={`${stats.active_users || 0} active sessions`} icon={Users} tone="emerald" />
                    <Kpi title="New Signups" value={stats.new_registrations || 0} caption="Created last 7 days" icon={UserCog} tone="cyan" />
                    <Kpi title="Total Revenue" value={`$${Number(stats.marketplace_revenue || 0).toLocaleString()}`} caption="Platform trade volume" icon={ShoppingBag} tone="purple" />
                    <Kpi title="ESG Impact" value={`${Number(stats.carbon_saved || 0).toLocaleString()} kg`} caption="Avoided carbon emissions" icon={Activity} tone="cyan" />
                    <Kpi title="Pending Moderation" value={stats.pending_listings || 0} caption={`${stats.approved_listings || 0} approved listings`} icon={ClipboardList} tone="amber" />
                    <Kpi title="AI Matches" value={stats.successful_matches || 0} caption={`${stats.pending_ai_matches || 0} weak recommendation pairs`} icon={Bot} tone="emerald" />
                    <Kpi title="Daily Orders" value={stats.transactions_today || 0} caption="Cleared transactions today" icon={FileSpreadsheet} tone="purple" />
                    <Kpi title="Storage Allocation" value={`${(stats.storage_usage || 0)} files`} caption="Enterprise secure storage" icon={Database} tone="purple" />
                  </div>

                  {/* Systems Overview */}
                  <div className="grid gap-6 md:grid-cols-3">
                    <ShellCard className="md:col-span-2 space-y-4">
                      <h3 className="text-lg font-black text-white flex items-center gap-2">
                        <Activity size={18} className="text-emerald-400" /> Regional Trade Activity
                      </h3>
                      <div className="grid gap-4 sm:grid-cols-3">
                        {(data.dashboard?.charts?.users_by_role || []).map((item) => (
                          <div key={item.label} className="rounded-2xl bg-slate-900/60 p-4 border border-slate-800">
                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{item.label}</p>
                            <p className="mt-2 text-2xl font-black text-white">{item.value}</p>
                            <div className="mt-3 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                              <div className="h-full bg-emerald-400" style={{ width: `${Math.min(100, item.value * 12)}%` }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </ShellCard>

                    <ShellCard className="space-y-4">
                      <h3 className="text-lg font-black text-white flex items-center gap-2">
                        <AlertTriangle size={18} className="text-amber-400" /> Platform Security Alerts
                      </h3>
                      <div className="space-y-3">
                        {(data.dashboard?.system_alerts || []).map((item, index) => (
                          <div key={index} className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-3 text-xs text-slate-300 flex items-start gap-2.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                            <span>{item.message}</span>
                          </div>
                        ))}
                      </div>
                    </ShellCard>
                  </div>
                </div>
              )}

              {/* Users Section */}
              {active === 'users' && (
                <ShellCard className="space-y-6">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <h3 className="text-lg font-black text-white">Identity Registry</h3>
                    <div className="flex flex-wrap gap-2">
                      <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs">
                        <Search size={14} className="text-slate-400" />
                        <input
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          className="bg-transparent outline-none text-slate-100 placeholder-slate-500 w-44"
                          placeholder="Search identity or name"
                        />
                      </div>
                      <select
                        value={roleFilter}
                        onChange={(e) => setRoleFilter(e.target.value)}
                        className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-300 outline-none"
                      >
                        <option value="">All Roles</option>
                        {roleOptions.map((role) => <option key={role} value={role}>{role}</option>)}
                      </select>
                      <ActionButton onClick={() => downloadExport('users', 'csv')}>CSV</ActionButton>
                      <ActionButton onClick={() => downloadExport('users', 'xlsx')}>Excel</ActionButton>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[900px] text-left text-sm">
                      <thead className="text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="py-3 font-semibold">User Identity</th>
                          <th className="py-3 font-semibold">Privilege Level</th>
                          <th className="py-3 font-semibold">Security Status</th>
                          <th className="py-3 font-semibold">Corp Verification</th>
                          <th className="py-3 font-semibold">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {visibleUsers.map((u) => (
                          <tr key={u.id} className="hover:bg-slate-900/20 transition">
                            <td className="py-4">
                              <p className="font-bold text-white">{u.full_name}</p>
                              <p className="text-xs text-slate-400">{u.email}</p>
                            </td>
                            <td>
                              <select
                                value={u.role}
                                onChange={(e) => runAction('User role modified', () => api.put(`/admin/users/${u.id}/role`, { role: e.target.value }))}
                                className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-300 outline-none"
                              >
                                {roleOptions.map((role) => <option key={role} value={role}>{role}</option>)}
                              </select>
                            </td>
                            <td>
                              <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                                u.is_active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                              }`}>
                                {u.is_active ? 'Active' : 'Suspended'}
                              </span>
                            </td>
                            <td>
                              <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                                u.email_verified ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                              }`}>
                                {u.email_verified ? 'Verified' : 'Unverified'}
                              </span>
                            </td>
                            <td className="py-3 flex flex-wrap gap-1.5">
                              <ActionButton onClick={() => setEditingUser(u)} tone="neutral">
                                <Edit2 size={13} /> Edit
                              </ActionButton>
                              <ActionButton
                                tone={u.is_active ? 'danger' : 'approve'}
                                onClick={() => runAction(u.is_active ? 'User suspended' : 'User activated', () => 
                                  api.put(`/admin/users/${u.id}/${u.is_active ? 'suspend' : 'activate'}`)
                                )}
                              >
                                {u.is_active ? 'Suspend' : 'Activate'}
                              </ActionButton>
                              <ActionButton
                                tone="warn"
                                onClick={() => {
                                  const temp = prompt('Set temporary password (leave blank for random):');
                                  if (temp !== null) {
                                    runAction('Password overridden', () => api.post(`/admin/users/${u.id}/reset-password`, { password: temp }));
                                  }
                                }}
                              >
                                Reset Pass
                              </ActionButton>
                              <ActionButton
                                tone={u.email_verified ? 'danger' : 'approve'}
                                onClick={() => runAction(u.email_verified ? 'Company rejected' : 'Company verified', () => 
                                  api.put(`/admin/users/${u.id}/company/${u.email_verified ? 'reject' : 'verify'}`)
                                )}
                              >
                                {u.email_verified ? 'Reject Corp' : 'Verify Corp'}
                              </ActionButton>
                              <ActionButton tone="danger" onClick={() => {
                                const confirmed = window.confirm(`Permanently delete ${u.email}? Their access and active sessions will be removed. They can return only by registering a new account.`);
                                if (confirmed) runAction('Account permanently deleted. The person must register again to access SymbioAI.', () => api.delete(`/admin/users/${u.id}`));
                              }}>
                                <Trash2 size={13} />
                              </ActionButton>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </ShellCard>
              )}

              {/* Companies Section */}
              {active === 'companies' && (
                <div className="space-y-6">
                  <ShellCard className="space-y-4">
                    <h3 className="text-lg font-black text-white">Registered Factories & Facilities</h3>
                    <div className="grid gap-4 sm:grid-cols-2">
                      {factories.map((f) => (
                        <div key={f.id} className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 space-y-3 flex flex-col justify-between">
                          <div>
                            <div className="flex items-start justify-between gap-2">
                              <h4 className="font-bold text-white">{f.name}</h4>
                              <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                                f.verified ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              }`}>
                                {f.verified ? 'Verified' : 'Pending'}
                              </span>
                            </div>
                            <p className="text-xs text-slate-400 mt-1">{f.industry} Sector Ã¢â‚¬â€ Location: {f.location}</p>
                            <p className="text-xs text-slate-500 mt-0.5">Owner ID: {f.owner_id}</p>
                          </div>

                          <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800/60">
                            <ActionButton
                              tone={f.verified ? 'danger' : 'approve'}
                              onClick={() => runAction(f.verified ? 'Factory verification revoked' : 'Factory verified', () => 
                                api.put(`/admin/factories/${f.id}/${f.verified ? 'reject' : 'verify'}`)
                              )}
                            >
                              {f.verified ? 'Revoke Verification' : 'Verify'}
                            </ActionButton>
                            <ActionButton onClick={() => fetchFactoryDocs(f.id)} tone="neutral">
                              <FileText size={13} /> View Documents
                            </ActionButton>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ShellCard>

                  {/* Company Documents Sub-Panel */}
                  {selectedFactoryDocs && (
                    <ShellCard className="space-y-4 border border-cyan-500/30">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-black text-white flex items-center gap-2">
                          <FileText size={18} className="text-cyan-400" /> Compliance certificates & licenses
                        </h3>
                        <ActionButton onClick={() => setSelectedFactoryDocs(null)} tone="danger">Close Documents</ActionButton>
                      </div>

                      {loadingDocs ? (
                        <div className="flex justify-center items-center py-8">
                          <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-800 border-t-cyan-400" />
                        </div>
                      ) : selectedFactoryDocs.length === 0 ? (
                        <p className="text-sm text-slate-400 py-4 italic">No compliance document records found for this facility.</p>
                      ) : (
                        <div className="grid gap-3 sm:grid-cols-2">
                          {selectedFactoryDocs.map((doc) => (
                            <div key={doc.id} className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-2">
                              <p className="text-sm font-bold text-white">{doc.document_name}</p>
                              <div className="text-xs text-slate-400 space-y-1">
                                <p>Type: <span className="text-slate-300 font-semibold">{doc.document_type}</span></p>
                                <p>Ref Number: <span className="text-slate-300">{doc.document_number}</span></p>
                                <p>Authority: <span className="text-slate-300">{doc.issuing_authority}</span></p>
                                <p>Status: <span className="text-emerald-400">{doc.status}</span></p>
                                <p>Expires: <span className="text-slate-300">{doc.expiry_date}</span></p>
                              </div>
                              {doc.document_url && (
                                <a
                                  href={doc.document_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs font-bold text-cyan-400 hover:underline block pt-2"
                                >
                                  Open Document Attachment &rarr;
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </ShellCard>
                  )}
                </div>
              )}

              {/* Listings Section */}
              {active === 'listings' && (
                <ShellCard className="space-y-6">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-black text-white">Listing Moderation</h3>
                      {selectedListings.length > 0 && (
                        <span className="text-xs font-bold text-cyan-400 animate-pulse bg-cyan-400/10 px-2 py-0.5 rounded-full border border-cyan-400/20">
                          {selectedListings.length} selected
                        </span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs">
                        <Search size={14} className="text-slate-400" />
                        <input
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          className="bg-transparent outline-none text-slate-100 placeholder-slate-500 w-44"
                          placeholder="Search material composition..."
                        />
                      </div>
                      <select
                        value={listingFilter}
                        onChange={(e) => setListingFilter(e.target.value)}
                        className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-300 outline-none"
                      >
                        <option value="">All Statuses</option>
                        {listingStatuses.map((st) => <option key={st} value={st}>{st}</option>)}
                      </select>
                      <ActionButton disabled={!selectedListings.length} onClick={() => bulkStatus('approved')} tone="approve">Bulk Approve</ActionButton>
                      <ActionButton disabled={!selectedListings.length} onClick={() => bulkStatus('rejected')} tone="danger">Bulk Reject</ActionButton>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {visibleListings.map((item) => (
                      <div
                        key={item.id}
                        className={`grid gap-4 rounded-2xl border p-5 transition duration-200 xl:grid-cols-[auto_1fr_auto] xl:items-center ${
                          selectedListings.includes(item.id) 
                            ? 'border-cyan-500/50 bg-cyan-500/5' 
                            : 'border-slate-800 bg-slate-900/30'
                        }`}
                      >
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            checked={selectedListings.includes(item.id)}
                            onChange={(e) => setSelectedListings((prev) => 
                              e.target.checked ? [...prev, item.id] : prev.filter((id) => id !== item.id)
                            )}
                            className="h-4 w-4 rounded border-slate-700 bg-slate-950 text-emerald-400 focus:ring-emerald-400 focus:ring-offset-slate-950 cursor-pointer"
                          />
                        </div>

                        <div>
                          <div className="flex flex-wrap items-center gap-2.5">
                            <h4 className="font-bold text-white text-base">{item.name}</h4>
                            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                              item.status === 'approved' 
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-400/20' 
                                : item.status === 'rejected' 
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-400/20'
                                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            }`}>
                              {item.status}
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 mt-1">
                            Quantity: <span className="text-slate-300 font-semibold">{item.quantity}</span> &bull; Frequency: <span className="text-slate-300">{item.frequency}</span>
                          </p>
                          <p className="text-xs text-slate-500 mt-0.5 truncate max-w-xl">Chemical: {item.chemical_composition}</p>
                          {item.certificate && <p className="text-xs text-emerald-400 mt-1">Certificate: {item.certificate}</p>}
                        </div>

                        <div className="flex flex-wrap gap-1.5 self-start xl:self-auto">
                          <ActionButton onClick={() => setEditingListing(item)} tone="neutral">
                            <Edit2 size={13} /> Edit
                          </ActionButton>
                          <ActionButton
                            tone="approve"
                            disabled={item.status === 'approved'}
                            onClick={() => runAction('Listing approved', () => api.put(`/admin/listings/${item.id}/status`, { status: 'approved' }))}
                          >
                            Approve
                          </ActionButton>
                          <ActionButton
                            tone="danger"
                            disabled={item.status === 'rejected'}
                            onClick={() => runAction('Listing rejected', () => api.put(`/admin/listings/${item.id}/status`, { status: 'rejected' }))}
                          >
                            Reject
                          </ActionButton>
                          <ActionButton
                            tone="warn"
                            disabled={item.status === 'flagged'}
                            onClick={() => runAction('Listing flagged', () => api.put(`/admin/listings/${item.id}/status`, { status: 'flagged' }))}
                          >
                            Flag
                          </ActionButton>
                          <ActionButton tone="danger" onClick={() => runAction('Listing deleted', () => api.delete(`/admin/listings/${item.id}`))}>
                            <Trash2 size={13} />
                          </ActionButton>
                        </div>
                      </div>
                    ))}
                  </div>
                </ShellCard>
              )}

              {/* Marketplace Section */}
              {['marketplace', 'transactions'].includes(active) && (
                <ShellCard className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-black text-white">Marketplace Transactions & Order Flow</h3>
                    <ActionButton onClick={() => downloadExport('transactions', 'csv')}>Export CSV</ActionButton>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[800px] text-left text-sm">
                      <thead className="text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="py-3 font-semibold">Transaction Reference</th>
                          <th className="py-3 font-semibold">Clearing Amount</th>
                          <th className="py-3 font-semibold">Settlement Status</th>
                          <th className="py-3 font-semibold">Override Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {transactions.map((tx) => (
                          <tr key={tx.id} className="hover:bg-slate-900/20 transition">
                            <td className="py-4">
                              <p className="font-bold text-white">{tx.partner_name}</p>
                              <p className="text-xs text-slate-500">Material ID: {tx.material_id}</p>
                            </td>
                            <td className="font-semibold text-slate-200">
                              ${Number(tx.amount || 0).toLocaleString()}
                            </td>
                            <td>
                              <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                                tx.status === 'Completed' 
                                  ? 'bg-emerald-500/10 text-emerald-400' 
                                  : tx.status === 'Disputed' 
                                  ? 'bg-rose-500/10 text-rose-400 animate-pulse'
                                  : 'bg-amber-500/10 text-amber-400'
                              }`}>
                                {tx.status}
                              </span>
                            </td>
                            <td>
                              <select
                                value={tx.status}
                                onChange={(e) => runAction('Transaction status updated', () => 
                                  api.put(`/admin/transactions/${tx.id}/status`, { status: e.target.value })
                                )}
                                className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-300 outline-none"
                              >
                                {txStatuses.map((st) => <option key={st} value={st}>{st}</option>)}
                              </select>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </ShellCard>
              )}

              {/* AI Engine Section */}
              {active === 'ai' && (
                <ShellCard className="space-y-6">
                  <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <h3 className="text-lg font-black text-white flex items-center gap-2">
                      <Bot className="text-emerald-400" /> AI Recommendation Settings
                    </h3>
                    <div className="flex items-center gap-3">
                      <label className="flex items-center gap-2 text-xs font-bold text-slate-300">
                        Confidence Threshold:
                        <input
                          type="number"
                          min="0"
                          max="100"
                          value={threshold}
                          onChange={(e) => setThreshold(e.target.value)}
                          className="w-20 rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-center text-slate-100 outline-none focus:border-emerald-400"
                        />
                      </label>
                      <ActionButton onClick={() => runAction('AI configuration updated', () => api.put('/admin/ai-matches/settings', { confidence_threshold: Number(threshold) }))}>
                        Update Threshold
                      </ActionButton>
                    </div>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    {matches.map((match) => (
                      <div key={match.id} className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 space-y-3 flex flex-col justify-between">
                        <div>
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="font-bold text-white">{match.partner_name}</h4>
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-black text-emerald-400 border border-emerald-400/20">
                              Score: {match.symbio_score}%
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 mt-1">Distance: {match.distance_km} km &bull; Savings: {match.carbon_savings}</p>
                          <p className="text-xs text-slate-300 mt-2 line-clamp-3 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/80 italic">{match.summary}</p>
                        </div>

                        <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800/60">
                          <ActionButton tone="approve" onClick={() => runAction('AI Match accepted', () => api.put(`/admin/ai-matches/${match.id}/accept`))}>
                            Accept Match
                          </ActionButton>
                          <ActionButton tone="warn" onClick={() => runAction('AI match logic re-run forced', () => api.put(`/admin/ai-matches/${match.id}/rematch`))}>
                            Force Rematch
                          </ActionButton>
                          <ActionButton tone="danger" onClick={() => runAction('AI Match rejected', () => api.put(`/admin/ai-matches/${match.id}/reject`))}>
                            Reject
                          </ActionButton>
                          <ActionButton tone="danger" onClick={() => runAction('AI Recommendation deleted', () => api.delete(`/admin/ai-matches/${match.id}`))}>
                            <Trash2 size={13} />
                          </ActionButton>
                        </div>
                      </div>
                    ))}
                  </div>
                </ShellCard>
              )}

              {/* Chat Moderation Section */}
              {active === 'chat' && (
                <ShellCard className="space-y-6">
                  <h3 className="text-lg font-black text-white">Abuse Moderation & Messaging Streams</h3>

                  <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
                    {/* Active Conversations */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Active Channels</h4>
                      {chat.conversations?.map((c) => (
                        <div key={c.id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-2">
                          <p className="font-bold text-white text-sm">{c.material_name}</p>
                          <div className="flex justify-between text-xs text-slate-400">
                            <span>Partner: {c.partner_name}</span>
                            <span>Status: {c.status}</span>
                          </div>
                          <div className="flex gap-2 pt-2">
                            <ActionButton tone="danger" onClick={() => runAction('User muted', () => api.put(`/admin/chat/mute/${c.seller_id}`))}>
                              Mute Seller
                            </ActionButton>
                            <ActionButton tone="danger" onClick={() => runAction('User banned from Chat', () => api.put(`/admin/chat/ban/${c.seller_id}`))}>
                              Ban Seller
                            </ActionButton>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Messages Flow */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Recent Messages</h4>
                      <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
                        {chat.messages?.map((m) => (
                          <div key={m.id} className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 space-y-2">
                            <div className="flex justify-between text-xs text-slate-400">
                              <span className="font-bold text-slate-300">{m.sender_name}</span>
                              <span>{new Date(m.created_at).toLocaleTimeString()}</span>
                            </div>
                            <p className="text-xs text-slate-200 bg-slate-950/30 p-2 rounded-lg border border-slate-800/40">{m.body}</p>
                            <ActionButton tone="danger" onClick={() => runAction('Message deleted from channel', () => api.delete(`/admin/chat/messages/${m.id}`))}>
                              Moderate Message
                            </ActionButton>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </ShellCard>
              )}

              {/* Reports Section */}
              {active === 'reports' && (
                <ShellCard className="space-y-6">
                  <h3 className="text-lg font-black text-white">Compliance & Financial Reporting Hub</h3>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {['users', 'transactions', 'listings', 'audit'].map((res) => (
                      <div key={res} className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
                        <h4 className="font-black text-white capitalize text-base">{res} Registry Report</h4>
                        <p className="text-xs text-slate-400">Generate and export verified datasets from {res} ledger records.</p>
                        <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800/60">
                          <ActionButton onClick={() => downloadExport(res, 'csv')}>CSV</ActionButton>
                          <ActionButton onClick={() => downloadExport(res, 'xlsx')}>Excel</ActionButton>
                          <ActionButton onClick={() => downloadExport(res, 'pdf')}>PDF Report</ActionButton>
                        </div>
                      </div>
                    ))}
                  </div>
                </ShellCard>
              )}

              {/* Analytics Section */}
              {active === 'analytics' && (
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {(data.dashboard?.charts?.revenue_heatmap || []).map((item) => (
                    <ShellCard key={item.label} className="space-y-4">
                      <div className="flex justify-between items-center">
                        <p className="font-bold text-white text-sm">{item.label}</p>
                        <span className="text-xs font-black text-emerald-400">${Number(item.value).toLocaleString()}</span>
                      </div>
                      <div className="h-28 rounded-2xl bg-gradient-to-t from-emerald-500/20 to-cyan-500/5 border border-slate-800 flex items-end p-4">
                        <div className="w-full bg-emerald-400 rounded-t-lg transition-all duration-500" style={{ height: `${Math.min(100, (item.value / 12000) * 100)}%` }} />
                      </div>
                      <p className="text-xs text-slate-400 italic">Clear density distribution score for target entity partners.</p>
                    </ShellCard>
                  ))}
                </div>
              )}

              {/* System Health Section */}
              {active === 'health' && (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {Object.entries(health).map(([key, val]) => (
                    <ShellCard key={key} className="space-y-4">
                      <div className="flex justify-between items-center">
                        <h4 className="font-black text-white capitalize">{key} Node</h4>
                        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
                          String(val.status).includes('healthy') || String(val.status).includes('configured') || String(val.status).includes('hardened')
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-400/20' 
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}>
                          {val.status}
                        </span>
                      </div>
                      <pre className="overflow-auto rounded-xl bg-slate-950 p-4 text-[10px] text-slate-400 font-mono leading-relaxed border border-slate-800">
                        {JSON.stringify(val, null, 2)}
                      </pre>
                    </ShellCard>
                  ))}
                </div>
              )}

              {/* Audit Logs Section */}
              {active === 'logs' && (
                <ShellCard className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-black text-white">Historical Security & Audit Trails</h3>
                    <ActionButton onClick={() => downloadExport('audit', 'csv')}>Export Audit Logs</ActionButton>
                  </div>

                  <div className="max-h-[500px] overflow-y-auto space-y-2 pr-2">
                    {(logs.audit_logs || []).map((log) => (
                      <div key={log.id} className="rounded-xl border border-slate-800 bg-slate-900/30 p-4 space-y-2 flex flex-col justify-between sm:flex-row sm:items-center sm:gap-4">
                        <div>
                          <p className="text-xs text-slate-400">{new Date(log.at).toLocaleString()}</p>
                          <p className="text-sm font-bold text-white mt-0.5">
                            Action: <span className="text-cyan-400">{log.action}</span> &bull; Object: <span className="text-slate-300">{log.entity_type}</span>
                          </p>
                          <p className="text-xs text-slate-500 mt-0.5">Entity ID Reference: {log.entity_id}</p>
                        </div>
                        <div className="text-right mt-2 sm:mt-0">
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-800 px-2.5 py-0.5 text-xs font-semibold text-slate-300 border border-slate-700">
                            {log.actor_role} ({log.ip_address || 'Internal Server'})
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ShellCard>
              )}

              {/* Notifications Section */}
              {active === 'notifications' && (
                <ShellCard className="space-y-6">
                  <h3 className="text-lg font-black text-white">Enterprise Global Notifications Dispatcher</h3>
                  <div className="grid gap-4">
                    <input
                      value={broadcast.title}
                      onChange={(e) => setBroadcast((v) => ({ ...v, title: e.target.value }))}
                      className="rounded-2xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-sm text-slate-100 outline-none focus:border-emerald-400"
                      placeholder="Enter global notification heading..."
                    />
                    <textarea
                      value={broadcast.message}
                      onChange={(e) => setBroadcast((v) => ({ ...v, message: e.target.value }))}
                      className="rounded-2xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-sm text-slate-100 outline-none focus:border-emerald-400"
                      rows="5"
                      placeholder="Write the announcement message content..."
                    />
                    <ActionButton
                      tone="primary"
                      onClick={() => runAction('Broadcast sent successfully to all operators', () => 
                        api.post('/admin/notifications/broadcast', broadcast)
                      )}
                    >
                      <Megaphone size={15} /> Dispatch Broadcast Message
                    </ActionButton>
                  </div>
                </ShellCard>
              )}

              {/* Settings Section */}
              {active === 'settings' && (
                <ShellCard className="space-y-6">
                  <h3 className="text-lg font-black text-white">System Settings & Configurations</h3>
                  <div className="grid gap-4 sm:grid-cols-2">
                    {Object.entries(data.settings || {}).map(([key, val]) => (
                      <div key={key} className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 space-y-1">
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">{key.replaceAll('_', ' ')}</p>
                        <p className="text-sm font-bold text-white">{String(val)}</p>
                      </div>
                    ))}
                  </div>
                  <div className="pt-4 border-t border-slate-800/60">
                    <ActionButton
                      tone="warn"
                      onClick={() => runAction('Settings audit state updated', () => 
                        api.put('/admin/settings', { reviewed_at: new Date().toISOString() })
                      )}
                    >
                      Record Configuration Audit Review
                    </ActionButton>
                  </div>
                </ShellCard>
              )}
            </>
          )}
        </main>
      </div>

      {/* Edit User Modal */}
      {editingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
          <ShellCard className="w-full max-w-md border border-cyan-500/30">
            <h3 className="text-lg font-black text-white">Edit User details</h3>
            <form onSubmit={handleEditUser} className="mt-4 space-y-4">
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">
                Full Name
                <input
                  type="text"
                  value={editingUser.full_name}
                  onChange={(e) => setEditingUser({ ...editingUser, full_name: e.target.value })}
                  className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
                  required
                />
              </label>

              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">
                Factory Logo URL
                <input
                  type="text"
                  value={editingUser.factory_logo_url || ''}
                  onChange={(e) => setEditingUser({ ...editingUser, factory_logo_url: e.target.value })}
                  className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
                />
              </label>

              <label className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider cursor-pointer">
                <input
                  type="checkbox"
                  checked={editingUser.email_verified}
                  onChange={(e) => setEditingUser({ ...editingUser, email_verified: e.target.checked })}
                  className="h-4 w-4 rounded border-slate-700 bg-slate-950 text-emerald-400 focus:ring-emerald-400"
                />
                Email & Company Verified
              </label>

              <div className="flex gap-2 pt-2 justify-end">
                <ActionButton onClick={() => setEditingUser(null)} tone="danger">Cancel</ActionButton>
                <ActionButton type="submit" tone="approve">Save Changes</ActionButton>
              </div>
            </form>
          </ShellCard>
        </div>
      )}

      {/* Edit Listing Modal */}
      {editingListing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
          <ShellCard className="w-full max-w-lg border border-cyan-500/30">
            <h3 className="text-lg font-black text-white">Modify Material Listing</h3>
            <form onSubmit={handleEditListing} className="mt-4 space-y-4">
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">
                Listing Name
                <input
                  type="text"
                  value={editingListing.name}
                  onChange={(e) => setEditingListing({ ...editingListing, name: e.target.value })}
                  className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
                  required
                />
              </label>

              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">
                Chemical Composition
                <textarea
                  value={editingListing.chemical_composition}
                  onChange={(e) => setEditingListing({ ...editingListing, chemical_composition: e.target.value })}
                  className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
                  rows="3"
                  required
                />
              </label>

              <div className="grid gap-3 sm:grid-cols-3">
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Physical State
                  <input
                    type="text"
                    value={editingListing.physical_state}
                    onChange={(e) => setEditingListing({ ...editingListing, physical_state: e.target.value })}
                    className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
                    required
                  />
                </label>

                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Quantity
                  <input
                    type="text"
                    value={editingListing.quantity}
                    onChange={(e) => setEditingListing({ ...editingListing, quantity: e.target.value })}
                    className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
                    required
                  />
                </label>

                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Frequency
                  <input
                    type="text"
                    value={editingListing.frequency}
                    onChange={(e) => setEditingListing({ ...editingListing, frequency: e.target.value })}
                    className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
                    required
                  />
                </label>
              </div>

              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">
                Certificate Title
                <input
                  type="text"
                  value={editingListing.certificate}
                  onChange={(e) => setEditingListing({ ...editingListing, certificate: e.target.value })}
                  className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
                  required
                />
              </label>

              <div className="flex gap-2 pt-2 justify-end">
                <ActionButton onClick={() => setEditingListing(null)} tone="danger">Cancel</ActionButton>
                <ActionButton type="submit" tone="approve">Save Changes</ActionButton>
              </div>
            </form>
          </ShellCard>
        </div>
      )}
    </div>
  );
}
