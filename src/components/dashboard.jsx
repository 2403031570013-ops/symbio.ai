import {
  ArrowRight,
  Factory,
  Leaf,
  Radar,
  Route,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';

const metrics = [
  { label: 'Revenue Generated', value: '$245K', change: '+18% vs last month' },
  { label: 'CO2 Avoided', value: '1,240 t', change: '+12% this quarter' },
  { label: 'Landfill Diversion', value: '3,820 t', change: '92% target achieved' },
  { label: 'AI Matches', value: '42', change: '6 new this week' },
];

const matches = [
  {
    name: 'Steel slag -> Cement blend',
    partner: 'Northstar Steel',
    score: '98%',
    impact: '1,200 t diverted',
  },
  {
    name: 'Process heat -> District network',
    partner: 'Harbor Chemicals',
    score: '94%',
    impact: '480 MWh recovered',
  },
  {
    name: 'Textile offcuts -> Insulation feedstock',
    partner: 'BlueLoop Textiles',
    score: '91%',
    impact: '360 t reused',
  },
];

const stages = [
  'Material verified',
  'Logistics optimized',
  'Carbon impact tracked',
];

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.25),_transparent_40%),linear-gradient(135deg,_#031427_0%,_#061b2c_55%,_#020812_100%)] text-slate-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <header className="rounded-3xl border border-emerald-400/20 bg-slate-900/70 p-6 shadow-2xl shadow-emerald-950/30 backdrop-blur-xl">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-sm font-medium text-emerald-300">
                <Leaf size={16} />
                Symbiotic Flux - Industrial symbiosis intelligence
              </div>
              <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Turn industrial waste into a circular revenue stream.
              </h1>
              <p className="mt-4 text-lg text-slate-300">
                SymbioAI connects waste producers and raw material consumers with AI-matched exchanges, verified sourcing, and live ESG reporting.
              </p>
            </div>
            <button className="inline-flex items-center justify-center gap-2 rounded-full bg-emerald-500 px-5 py-3 font-semibold text-slate-950 transition hover:bg-emerald-400">
              Explore marketplace
              <ArrowRight size={18} />
            </button>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-lg shadow-slate-950/20">
              <p className="text-sm text-slate-400">{metric.label}</p>
              <p className="mt-2 text-3xl font-semibold text-white">{metric.value}</p>
              <p className="mt-2 text-sm text-emerald-300">{metric.change}</p>
            </div>
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-300">AI matching</p>
                <h2 className="text-2xl font-semibold text-white">High-confidence material exchanges</h2>
              </div>
              <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 p-3 text-emerald-300">
                <Radar size={20} />
              </div>
            </div>

            <div className="space-y-4">
              {matches.map((match) => (
                <div key={match.name} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="font-semibold text-white">{match.name}</p>
                      <p className="text-sm text-slate-400">{match.partner}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-emerald-300">Match score {match.score}</p>
                      <p className="text-sm text-slate-400">{match.impact}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
              <div className="mb-4 flex items-center gap-3">
                <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 p-3 text-emerald-300">
                  <ShieldCheck size={20} />
                </div>
                <div>
                  <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-300">Verified source</p>
                  <h3 className="text-xl font-semibold text-white">Audited industrial partners</h3>
                </div>
              </div>
              <p className="text-sm leading-6 text-slate-400">
                Verified source badges help buyers trust chemical composition, sustainability practices, and repeatable supply.
              </p>
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
              <div className="mb-4 flex items-center gap-3">
                <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 p-3 text-emerald-300">
                  <Route size={20} />
                </div>
                <div>
                  <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-300">Logistics</p>
                  <h3 className="text-xl font-semibold text-white">Route optimization</h3>
                </div>
              </div>
              <div className="space-y-3">
                {stages.map((stage) => (
                  <div key={stage} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2 text-sm text-slate-300">
                    <span>{stage}</span>
                    <TrendingUp size={16} className="text-emerald-300" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1fr_0.75fr]">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 p-3 text-emerald-300">
                <Factory size={20} />
              </div>
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-300">Marketplace roles</p>
                <h3 className="text-xl font-semibold text-white">Built for producers, buyers, and admins</h3>
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {['Waste Producer', 'Raw Material Consumer', 'Platform Admin'].map((role) => (
                <div key={role} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-300">
                  <p className="font-semibold text-white">{role}</p>
                  <p className="mt-2">Manage listings, verify supply, and coordinate carbon reporting in one view.</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-emerald-400/20 bg-emerald-500/10 p-6 shadow-xl backdrop-blur">
            <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-300">Next milestone</p>
            <h3 className="mt-2 text-2xl font-semibold text-white">Phase 2 automation is ready to launch</h3>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              This experience now reflects the core MVP priorities: marketplace matching, sustainability metrics, and logistics oversight.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
