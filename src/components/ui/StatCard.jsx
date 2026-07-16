export default function StatCard({ label, value, trend, accent = 'emerald' }) {
  const accentClasses = {
    emerald: 'text-emerald-300',
    blue: 'text-sky-300',
    violet: 'text-violet-300',
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.07] p-5 shadow-lg shadow-slate-950/20 backdrop-blur transition duration-300 hover:-translate-y-0.5 hover:border-emerald-300/20">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white sm:text-3xl">{value}</p>
      <p className={`mt-2 text-sm ${accentClasses[accent]}`}>{trend}</p>
    </div>
  );
}
