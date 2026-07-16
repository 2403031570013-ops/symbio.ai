export default function ChartCard({ title, caption, children }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.07] p-5 shadow-xl shadow-slate-950/25 backdrop-blur-xl transition duration-300 hover:border-emerald-300/20 sm:p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="text-sm text-slate-400">{caption}</p>
      </div>
      {children}
    </div>
  );
}
