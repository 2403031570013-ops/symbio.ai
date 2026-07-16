import { ArrowRight, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatCard from '../components/ui/StatCard';
import PageHeader from '../components/ui/PageHeader';
import ChartCard from '../components/ui/ChartCard';
import { dashboardStats, sustainabilitySeries, recentTransactions, aiMatches } from '../services/dummyData';

export default function DashboardPage() {
  const navigate = useNavigate();

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
            {recentTransactions.map((transaction) => (
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
            ))}
          </div>
        </ChartCard>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.85fr]">
        <ChartCard title="Recent AI matches" caption="Matches generated from your material catalog">
          <div className="space-y-4">
            {aiMatches.map((match) => (
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
            ))}
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
