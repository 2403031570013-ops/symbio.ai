import { useState, useEffect } from 'react';
import { DollarSign, Bell, Zap, FileText, BarChart3, AlertCircle, TrendingUp } from 'lucide-react';
import api from '../services/api';
import { getApiError, unwrapList } from '../services/response';

export default function MarketplacePage() {
  const [notifications, setNotifications] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setError('');
    try {
      const [notifResp, contractResp, paymentResp] = await Promise.all([
        api.get('/marketplace/smart-notifications'),
        api.get('/marketplace/contracts/factory-id'),
        api.get('/marketplace/payments/factory-id')
      ]);
      setNotifications(unwrapList(notifResp));
      setContracts(unwrapList(contractResp));
      setPayments(unwrapList(paymentResp));
    } catch (err) {
      console.error('Failed to fetch marketplace data:', err);
      setError(getApiError(err, 'Unable to load marketplace data'));
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.put(`/marketplace/smart-notifications/${id}/read`);
      fetchData();
    } catch (err) {
      setError(getApiError(err, 'Failed to mark notification as read'));
    }
  };

  if (loading) {
    return <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 text-slate-300">Loading marketplace...</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {error ? <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Marketplace & Operations</h1>
        <p className="text-slate-300">Manage contracts, payments, notifications, and automation</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Smart Notifications</h3>
            <Bell className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-3">
            {notifications.length === 0 ? <p className="text-sm text-gray-500">No notifications yet.</p> : null}
            {notifications.slice(0, 5).map((notif) => (
              <div key={notif.id} className={`p-3 rounded-lg ${notif.status === 'unread' ? 'bg-blue-50' : 'bg-gray-50'}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 text-sm">{notif.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{notif.message}</p>
                  </div>
                  {notif.status === 'unread' ? (
                    <button onClick={() => markAsRead(notif.id)} className="ml-2 text-blue-600 hover:text-blue-800" aria-label="Mark notification as read">
                      <Zap className="w-4 h-4" />
                    </button>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Active Contracts</h3>
            <FileText className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-3">
            {contracts.length === 0 ? <p className="text-sm text-gray-500">No active contracts yet.</p> : null}
            {contracts.slice(0, 5).map((contract) => (
              <div key={contract.id} className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium text-gray-900 text-sm">{contract.contract_number}</p>
                <p className="text-xs text-gray-600 mt-1">{contract.contract_type}</p>
                <p className="text-sm font-medium text-green-600 mt-2">${Number(contract.value || 0).toLocaleString()}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Payments</h3>
            <DollarSign className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-3">
            {payments.length === 0 ? <p className="text-sm text-gray-500">No payments recorded yet.</p> : null}
            {payments.slice(0, 5).map((payment) => (
              <div key={payment.id} className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium text-gray-900 text-sm">{payment.reference_number || payment.invoice_number}</p>
                <p className="text-xs text-gray-600 mt-1">{payment.payment_method}</p>
                <p className="text-sm font-medium text-blue-600 mt-2">${Number(payment.amount || 0).toLocaleString()}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Dynamic Pricing</h3>
            <BarChart3 className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <div>
                <p className="text-sm text-green-600">Price Optimization</p>
                <p className="text-2xl font-bold text-green-900">+12.5%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div>
                <p className="text-sm text-blue-600">Demand Match</p>
                <p className="text-2xl font-bold text-blue-900">94%</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Workflow Automation</h3>
            <Zap className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-3">
            {[
              ['Auto-match materials', 'Running', 'Active', 'text-green-600'],
              ['Price alerts', 'Running', 'Active', 'text-blue-600'],
              ['Compliance checks', 'Paused', 'Paused', 'text-yellow-600'],
            ].map(([name, detail, status, color]) => (
              <div key={name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <AlertCircle className={`w-4 h-4 ${color}`} />
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{name}</p>
                    <p className="text-xs text-gray-600">{detail}</p>
                  </div>
                </div>
                <span className={`${color} text-sm`}>{status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}