import { useEffect, useState } from 'react';
import { AlertCircle, MapPin, Package, RefreshCw, TrendingUp, Truck } from 'lucide-react';
import api from '../services/api';
import { getApiError, unwrapList } from '../services/response';

const stockStyles = {
  critical: 'bg-red-100 text-red-800',
  low: 'bg-yellow-100 text-yellow-800',
  overstocked: 'bg-blue-100 text-blue-800',
  normal: 'bg-green-100 text-green-800',
};

function getStockStatus(status) {
  switch (status) {
    case 'critical':
      return { key: 'critical', text: 'Critical' };
    case 'low':
      return { key: 'low', text: 'Low Stock' };
    case 'overstocked':
      return { key: 'overstocked', text: 'Overstocked' };
    default:
      return { key: 'normal', text: 'Normal' };
  }
}

function normalizeShipment(shipment) {
  return {
    id: shipment.id,
    origin: shipment.origin || shipment.partner_name || 'Source factory',
    destination: shipment.destination || 'Receiving factory',
    status: shipment.status || 'scheduled',
  };
}

export default function SupplyChainPage() {
  const [inventory, setInventory] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [invResp, shipResp] = await Promise.all([
        api.get('/supply-chain/inventory/factory-id'),
        api.get('/shipments'),
      ]);
      setInventory(unwrapList(invResp));
      setShipments(unwrapList(shipResp, 'shipments').map(normalizeShipment));
    } catch (err) {
      console.error('Failed to fetch supply chain data:', err);
      setError(getApiError(err, 'Unable to load supply chain data'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 text-slate-300">
        Loading supply chain...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.3em] text-emerald-300">Supply Chain</p>
            <h1 className="mt-2 text-3xl font-bold text-white">Supply Chain Management</h1>
            <p className="mt-2 text-slate-400">Real-time inventory, shipment status, and route optimization.</p>
          </div>
          <button
            type="button"
            onClick={fetchData}
            className="inline-flex items-center gap-2 rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {error ? (
        <div className="flex items-start gap-3 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Inventory Status</h3>
            <Package className="h-5 w-5 text-emerald-300" />
          </div>
          <div className="space-y-3">
            {inventory.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-700 p-5 text-sm text-slate-400">
                No inventory records yet.
              </div>
            ) : null}
            {inventory.slice(0, 5).map((item) => {
              const status = getStockStatus(item.stock_status);
              return (
                <div key={item.id} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <div>
                    <p className="font-medium text-white">{item.material_id}</p>
                    <p className="text-sm text-slate-400">{item.current_stock} units available</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-medium ${stockStyles[status.key]}`}>
                    {status.text}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Active Shipments</h3>
            <Truck className="h-5 w-5 text-emerald-300" />
          </div>
          <div className="space-y-3">
            {shipments.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-700 p-5 text-sm text-slate-400">
                No active shipments yet.
              </div>
            ) : null}
            {shipments.slice(0, 5).map((shipment) => (
              <div key={shipment.id} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="flex items-center gap-3">
                  <MapPin className="h-4 w-4 text-slate-400" />
                  <div>
                    <p className="font-medium text-white">{shipment.origin}</p>
                    <p className="text-sm text-slate-400">to {shipment.destination}</p>
                  </div>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-medium ${
                  shipment.status === 'in_transit' || shipment.status === 'In transit' ? 'bg-blue-100 text-blue-800' :
                  shipment.status === 'delivered' || shipment.status === 'Delivered' ? 'bg-green-100 text-green-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {shipment.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-slate-950/25">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Route Optimization</h3>
          <TrendingUp className="h-5 w-5 text-emerald-300" />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-4">
            <p className="text-sm text-emerald-300">Distance Saved</p>
            <p className="mt-1 text-2xl font-bold text-white">1,234 km</p>
          </div>
          <div className="rounded-2xl border border-sky-400/20 bg-sky-500/10 p-4">
            <p className="text-sm text-sky-300">Time Saved</p>
            <p className="mt-1 text-2xl font-bold text-white">45 hrs</p>
          </div>
          <div className="rounded-2xl border border-violet-400/20 bg-violet-500/10 p-4">
            <p className="text-sm text-violet-300">CO2 Saved</p>
            <p className="mt-1 text-2xl font-bold text-white">234 kg</p>
          </div>
        </div>
      </div>
    </div>
  );
}
