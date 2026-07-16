import { useState, useEffect } from 'react';
import { Leaf, Droplet, Wind, Award, TrendingUp } from 'lucide-react';
import api from '../services/api';

export default function ESGDashboardPage() {
  const [esgData, setEsgData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchESGData();
  }, []);

  const fetchESGData = async () => {
    try {
      const response = await api.get('/esg/sustainability-dashboard/factory-id');
      setEsgData(response.data);
    } catch (error) {
      console.error('Failed to fetch ESG data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">ESG Dashboard</h1>
        <p className="text-gray-600">Environmental, Social, and Governance metrics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <Leaf className="w-8 h-8 text-green-600" />
            <span className="text-sm text-gray-500">CO2 Saved</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{esgData?.total_co2_saved || 0} kg</p>
          <p className="text-sm text-green-600 mt-2">↑ 12% from last month</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <Droplet className="w-8 h-8 text-blue-600" />
            <span className="text-sm text-gray-500">Water Saved</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{esgData?.water_saved || 0} L</p>
          <p className="text-sm text-blue-600 mt-2">↑ 8% from last month</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <Wind className="w-8 h-8 text-purple-600" />
            <span className="text-sm text-gray-500">Energy Saved</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{esgData?.energy_saved || 0} kWh</p>
          <p className="text-sm text-purple-600 mt-2">↑ 15% from last month</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <Award className="w-8 h-8 text-yellow-600" />
            <span className="text-sm text-gray-500">ESG Score</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{esgData?.circular_economy_score || 0}/100</p>
          <p className="text-sm text-yellow-600 mt-2">Top 10% in industry</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Waste Diversion</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-600">Recycling Rate</span>
                <span className="text-sm font-medium">{esgData?.recycling_rate || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{ width: `${esgData?.recycling_rate || 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-600">Circular Economy</span>
                <span className="text-sm font-medium">{esgData?.circular_economy_score || 0}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${esgData?.circular_economy_score || 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Certifications</h3>
          <div className="space-y-3">
            {esgData?.zero_waste_certified && (
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                <Award className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium text-green-900">Zero Waste Certified</p>
                  <p className="text-sm text-green-700">Industry recognized</p>
                </div>
              </div>
            )}
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <div>
                <p className="font-medium text-blue-900">Carbon Neutral</p>
                <p className="text-sm text-blue-700">Net-zero emissions achieved</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
