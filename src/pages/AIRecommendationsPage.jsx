import { useEffect, useState } from 'react';
import { AlertTriangle, Brain, DollarSign, TrendingUp } from 'lucide-react';
import api from '../services/api';
import { getApiError, unwrapData } from '../services/response';

const dummyRecommendations = [
  {
    id: 'demo-rec-1',
    recommendation_type: 'material',
    title: 'Convert steel slag into cement additive',
    description: 'Northstar Cement can use your slag stream as a clinker substitute with strong CO2 reduction potential.',
    confidence_score: 0.94,
    expected_benefit: { cost_savings: 18400 },
    status: 'pending',
    demo: true,
  },
  {
    id: 'demo-rec-2',
    recommendation_type: 'pricing',
    title: 'Increase fly ash contract price by 8%',
    description: 'Demand signals and regional inventory suggest buyers can absorb a moderate price increase this month.',
    confidence_score: 0.87,
    expected_benefit: { cost_savings: 9200 },
    status: 'pending',
    demo: true,
  },
  {
    id: 'demo-rec-3',
    recommendation_type: 'route',
    title: 'Bundle shipment with nearby textile offcuts route',
    description: 'Combining two compatible pickups can reduce empty return distance and logistics emissions.',
    confidence_score: 0.82,
    expected_benefit: { cost_savings: 5100 },
    status: 'pending',
    demo: true,
  },
];

export default function AIRecommendationsPage() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setError('');
      const response = await api.get('/ai/recommendations');
      const data = unwrapData(response);
      const loaded = data?.recommendations || (Array.isArray(data) ? data : []);
      setRecommendations(loaded.length ? loaded : dummyRecommendations);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      setError(getApiError(err, 'Showing demo AI recommendations because live recommendations could not load'));
      setRecommendations(dummyRecommendations);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (id, status) => {
    const target = recommendations.find((rec) => rec.id === id);
    if (target?.demo) {
      setRecommendations((prev) => prev.map((rec) => rec.id === id ? { ...rec, status } : rec));
      return;
    }

    try {
      await api.put(`/ai/recommendations/${id}/status`, null, { params: { status } });
      fetchRecommendations();
    } catch (err) {
      console.error('Failed to update status:', err);
      setError(getApiError(err, 'Unable to update recommendation'));
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'material': return <Brain className="w-5 h-5" />;
      case 'pricing': return <DollarSign className="w-5 h-5" />;
      case 'route': return <TrendingUp className="w-5 h-5" />;
      default: return <AlertTriangle className="w-5 h-5" />;
    }
  };

  if (loading) {
    return <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 text-slate-300">Loading AI recommendations...</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {error ? <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{error}</div> : null}

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">AI Recommendations</h1>
        <p className="text-slate-300">AI-powered insights to optimize your operations</p>
      </div>

      <div className="grid gap-4">
        {recommendations.map((rec) => (
          <div key={rec.id} className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-100 rounded-lg text-blue-600">
                  {getIcon(rec.recommendation_type)}
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-gray-900 mb-1">{rec.title}</h3>
                    {rec.demo ? <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-800">Demo</span> : null}
                  </div>
                  <p className="text-gray-600 text-sm mb-3">{rec.description}</p>
                  <div className="flex flex-wrap items-center gap-4 text-sm">
                    <span className="text-gray-500">Confidence: {Math.round(Number(rec.confidence_score || 0) * 100)}%</span>
                    {rec.expected_benefit ? <span className="text-green-600">${Number(rec.expected_benefit.cost_savings || 0).toLocaleString()} savings</span> : null}
                  </div>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {rec.status === 'pending' ? (
                  <>
                    <button onClick={() => handleStatusUpdate(rec.id, 'accepted')} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">Accept</button>
                    <button onClick={() => handleStatusUpdate(rec.id, 'rejected')} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">Reject</button>
                  </>
                ) : null}
                <span className={`px-3 py-2 rounded-full text-sm ${
                  rec.status === 'accepted' ? 'bg-green-100 text-green-800' :
                  rec.status === 'rejected' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {rec.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
