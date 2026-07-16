import { Download } from 'lucide-react';
import PageHeader from '../components/ui/PageHeader';
import ChartCard from '../components/ui/ChartCard';
import { analyticsBreakdown, dashboardStats, sustainabilitySeries } from '../services/dummyData';

function downloadFile(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export default function EsgAnalyticsPage() {
  const exportCsv = () => {
    const rows = [
      ['Metric', 'Value', 'Trend'],
      ...dashboardStats.map((stat) => [stat.label, stat.value, stat.trend]),
      [],
      ['Month', 'CO2 Avoided Index', 'Revenue Index'],
      ...sustainabilitySeries.map((point, index) => [point.month, point.value, [48, 59, 72, 81, 94, 110][index]]),
      [],
      ['Circular Economy Area', 'Score'],
      ...analyticsBreakdown.map((item) => [item.label, `${item.value}%`]),
    ];
    const csv = rows.map((row) => row.map((cell) => `"${String(cell ?? '').replaceAll('"', '""')}"`).join(',')).join('\n');
    downloadFile('symbioai-esg-report.csv', csv, 'text/csv;charset=utf-8');
  };

  const exportPdf = () => {
    const html = `<!doctype html><html><head><title>SymbioAI ESG Report</title><style>body{font-family:Arial,sans-serif;padding:32px;color:#0f172a}h1{color:#047857}.card{border:1px solid #d1d5db;border-radius:12px;padding:16px;margin:12px 0}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.muted{color:#64748b}</style></head><body><h1>SymbioAI ESG Report</h1><p class="muted">Generated from ESG analytics dashboard.</p><div class="grid">${dashboardStats.map((stat) => `<div class="card"><h3>${stat.label}</h3><p><strong>${stat.value}</strong></p><p>${stat.trend}</p></div>`).join('')}</div><h2>CO2 Avoided Trend</h2>${sustainabilitySeries.map((point) => `<div class="card">${point.month}: ${point.value}</div>`).join('')}<h2>Circular Economy Score</h2>${analyticsBreakdown.map((item) => `<div class="card">${item.label}: ${item.value}%</div>`).join('')}<script>window.print()</script></body></html>`;
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="ESG analytics"
        description="Generate investor-grade sustainability reports and carbon diversion insights."
        action={
          <div className="flex gap-3">
            <button type="button" onClick={exportCsv} className="rounded-full border border-slate-700 bg-slate-950/70 px-4 py-2 text-sm text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300">
              Export CSV
            </button>
            <button type="button" onClick={exportPdf} className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400">
              <Download size={16} />
              Export PDF
            </button>
          </div>
        }
      />

      <section className="grid gap-6 lg:grid-cols-2">
        <ChartCard title="CO2 reduction" caption="Thermal and material diversion impact">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
            <div className="flex h-40 items-end gap-3">
              {[68, 84, 72, 91, 96, 104].map((height, index) => (
                <div key={index} className="flex flex-1 flex-col items-center gap-2">
                  <div className="w-full rounded-t-xl bg-gradient-to-t from-emerald-500 to-emerald-300" style={{ height: `${height}px` }} />
                </div>
              ))}
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Revenue trends" caption="Quarterly exchange revenue and margin growth">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
            <div className="flex h-40 items-end gap-3">
              {[48, 59, 72, 81, 94, 110].map((height, index) => (
                <div key={index} className="flex flex-1 flex-col items-center gap-2">
                  <div className="w-full rounded-t-xl bg-gradient-to-t from-sky-500 to-sky-300" style={{ height: `${height}px` }} />
                </div>
              ))}
            </div>
          </div>
        </ChartCard>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
        <ChartCard title="Circular economy score" caption="Composite score across material loops and impact">
          <div className="space-y-4">
            {analyticsBreakdown.map((item) => (
              <div key={item.label} className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="mb-2 flex items-center justify-between text-sm text-slate-400">
                  <span>{item.label}</span>
                  <span>{item.value}%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-800">
                  <div className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-emerald-300" style={{ width: `${item.value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </ChartCard>

        <div className="rounded-3xl border border-emerald-400/20 bg-emerald-500/10 p-6 shadow-xl shadow-slate-950/25">
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-300">Impact summary</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">89% of waste diverted this year</h3>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Your current portfolio outperforms the median circularity benchmark for industrial ecosystems.
          </p>
        </div>
      </section>
    </div>
  );
}
