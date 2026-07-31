import { useEffect, useState } from 'react';
import { CreditCard, PackageCheck, ShieldCheck } from 'lucide-react';
import PageHeader from '../components/ui/PageHeader';
import api from '../services/api';
import { getApiError, unwrapData } from '../services/response';

export default function TransactionsPage() {
  const [shipments, setShipments] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    api.get('/shipments')
      .then((response) => {
        if (!active) return;
        setShipments((unwrapData(response)?.shipments || []).map((shipment, index) => ({
          title: shipment.partner_name ? `Shipment to ${shipment.partner_name}` : `Shipment ${index + 1}`,
          detail: shipment.status ? `Current status: ${shipment.status}` : 'Current status pending',
          time: shipment.updated_at ? new Date(shipment.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Now',
        })));
      })
      .catch((requestError) => {
        if (!active) return;
        setError(getApiError(requestError, 'Unable to load shipments'));
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Transactions hub"
        description="Monitor shipment progress, quality verification, and payment status in real time."
      />

      {error ? <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">{error}</div> : null}

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 p-3 text-emerald-300">
              <PackageCheck size={18} />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Shipment timeline</h2>
              <p className="text-sm text-slate-400">Live routing and handling updates</p>
            </div>
          </div>

          <div className="space-y-4">
            {shipments.length ? shipments.map((item, index) => (
              <div key={item.title} className="flex gap-3 rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="mt-1 h-3 w-3 rounded-full bg-emerald-400" />
                <div className="flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-white">{item.title}</p>
                    <span className="text-sm text-slate-400">{item.time}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-400">{item.detail}</p>
                  {index === 1 ? <p className="mt-2 text-sm text-emerald-300">Quality verification status: Approved</p> : null}
                </div>
              </div>
            )) : <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">No shipments yet. Transactions will appear here once created.</div>}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 p-3 text-emerald-300">
                <ShieldCheck size={18} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Quality verification</h3>
                <p className="text-sm text-slate-400">Lab and compliance review</p>
              </div>
            </div>
            <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-4 text-sm text-emerald-300">
              Verified by certified lab • 98.6% sample integrity
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 p-3 text-emerald-300">
                <CreditCard size={18} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Payment status</h3>
                <p className="text-sm text-slate-400">Invoice processing and settlement</p>
              </div>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-300">
              Pending settlement • 3 business days remaining
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
