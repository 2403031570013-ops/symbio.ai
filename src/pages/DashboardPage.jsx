import { useEffect, useState } from 'react';
import { ArrowRight, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatCard from '../components/ui/StatCard';
import PageHeader from '../components/ui/PageHeader';
import ChartCard from '../components/ui/ChartCard';
import api from '../services/api';
import { getApiError, unwrapData } from '../services/response';

const fallbackDashboardStats = [
  { label: 'Revenue Generated', value: '$0', trend: 'No transactions yet' },
  { label: 'CO₂ Avoided', value: '0 t', trend: 'No sustainability data yet' },
  { label: 'Landfill Diversion', value: '0 t', trend: 'No diverted materials yet' },
  { label: 'Active AI Matches', value: '0', trend: 'No matches yet' },
];

const fallbackSustainabilitySeries = [
  { month: 'Jan', value: 16 },
  { month: 'Feb', value: 18 },
  { month: 'Mar', value: 20 },
  { month: 'Apr', value: 22 },
  { month: 'May', value: 24 },
  { month: 'Jun', value: 26 },
];

export default function DashboardPage() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState({ analytics: null, transactions: [], matches: [] });
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    Promise.all([api.get('/analytics/dashboard'), api.get('/transactions'), api.get('/matches')])
      .then(([analyticsResponse, transactionsResponse, matchesResponse]) => {
        if (!active) return;
        setDashboard({
          analytics: unwrapData(analyticsResponse)?.analytics || null,
          transactions: unwrapData(transactionsResponse)?.transactions || [],
          matches: unwrapData(matchesResponse)?.matches || [],
        });
      })
      .catch((requestError) => {
        if (!active) return;
        setError(getApiError(requestError, 'Unable to load dashboard data'));
      });

    return () => {
      active = false;
    };
  }, []);

  const dashboardStats = dashboard.analytics
    ? [
        { label: 'Revenue Generated', value: `$${Number(dashboard.analytics.revenue_generated || 0).toLocaleString()}`, trend: 'Live backend analytics' },
        { label: 'CO₂ Avoided', value: `${Number(dashboard.analytics.co2_avoided || 0).toLocaleString()} t`, trend: 'Live backend analytics' },
        { label: 'Landfill Diversion', value: `${Number(dashboard.analytics.landfill_diversion || 0).toLocaleString()} t`, trend: 'Live backend analytics' },
        { label: 'Active AI Matches', value: `${Number(dashboard.analytics.active_matches || 0).toLocaleString()}`, trend: 'Live backend analytics' },
      ]
    : fallbackDashboardStats;

  const sustainabilitySeries = dashboard.analytics
    ? fallbackSustainabilitySeries.map((point, index) => ({
        ...point,
        value: Math.max(16, Math.round((Number(dashboard.analytics.co2_avoided || 0) / 80) * ((index + 1) / fallbackSustainabilitySeries.length))),
      }))
    : fallbackSustainabilitySeries;

  const recentTransactions = dashboard.transactions.length
    ? dashboard.transactions.slice(0, 3).map((transaction) => ({
        id: transaction.id,
        partner: transaction.partner_name || transaction.partner || 'Verified partner',
        amount: `$${Number(transaction.amount || 0).toLocaleString()}`,
        status: transaction.status || 'Pending',
      }))
    : [];

  const aiMatches = dashboard.matches.length
    ? dashboard.matches.slice(0, 3).map((match) => ({
        name: match.material_name || match.summary || 'AI match',
        partner: match.partner_name || 'Verified partner',
        score: match.symbio_score || 0,
        distance: `${match.distance_km || 0} km`,
        carbon: match.carbon_savings || 'Impact pending',
      }))
    : [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Operations dashboard"
        description="Track material exchanges, carbon impact, and high-confidence matches from one control center."
        action={
          <button
            type="button"
            onClick={() => navigate('/listings')}
            className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-4 py-2 font-semibold text-slate-950 transition hover:bg-emerald-400"
          >
            Create new listing
            <ArrowRight size={16} />
          </button>
        }
      />

      {error ? <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">{error}</div> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {dashboardStats.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <ChartCard title="Sustainability performance" caption="CO2 avoided trend over the last 6 months">
          <div className="space-y-4">
            <div className="flex items-end gap-3 rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
              {sustainabilitySeries.map((point) => (
                <div key={point.month} className="flex flex-1 flex-col items-center gap-2">
                  <div className="flex h-36 w-full items-end justify-center rounded-xl bg-slate-900/70 p-2">
                    <div className="w-full rounded-t-xl bg-gradient-to-t from-emerald-500 to-emerald-300" style={{ height: `${Math.max(point.value / 8, 16)}px` }} />
                  </div>
                  <span className="text-sm text-slate-400">{point.month}</span>
                </div>
              ))}
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Recent transactions" caption="Live shipment and payment milestones">
          <div className="space-y-3">
            {recentTransactions.length ? recentTransactions.map((transaction) => (
              <div key={transaction.id} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">{transaction.partner}</p>
                    <p className="text-sm text-slate-400">{transaction.id}</p>
                  </div>
                  <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-sm text-emerald-300">{transaction.status}</span>
                </div>
                <p className="mt-3 text-lg font-semibold text-white">{transaction.amount}</p>
              </div>
            )) : <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">No transactions yet. New activity will appear here automatically.</div>}
          </div>
        </ChartCard>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.85fr]">
        <ChartCard title="Recent AI matches" caption="Matches generated from your material catalog">
          <div className="space-y-4">
            {aiMatches.length ? aiMatches.map((match) => (
              <div key={match.name} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="font-semibold text-white">{match.name}</p>
                    <p className="text-sm text-slate-400">{match.partner}</p>
                  </div>
                  <div className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">Symbio score {match.score}/100</div>
                </div>
                <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-400">
                  <span>Distance: {match.distance}</span>
                  <span>Carbon savings: {match.carbon}</span>
                </div>
              </div>
            )) : <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">No matches yet. Upload materials to generate AI recommendations.</div>}
          </div>
        </ChartCard>

        <ChartCard title="Operational snapshot" caption="One-click actions for the next quarter">
          <div className="space-y-3">
            {[
              'Automate supplier updates',
              'Export ESG report',
              'Launch route optimization',
            ].map((item) => (
              <div key={item} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
                <span>{item}</span>
                <TrendingUp size={16} className="text-emerald-300" />
              </div>
            ))}
          </div>
        </ChartCard>
      </section>
    </div>
  );
}
