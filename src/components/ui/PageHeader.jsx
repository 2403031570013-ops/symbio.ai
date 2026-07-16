export default function PageHeader({ title, description, action }) {
  return (
    <div className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/[0.07] p-5 shadow-xl shadow-slate-950/25 backdrop-blur-xl transition duration-300 hover:border-emerald-300/20 sm:p-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-300 sm:text-sm">SymbioAI</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">{title}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">{description}</p>
      </div>
      {action}
    </div>
  );
}
