import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, FileText, CheckCircle, Clock } from 'lucide-react';
import api from '../services/api';

export default function CompliancePage() {
  const [complianceChecks, setComplianceChecks] = useState([]);
  const [riskAssessments, setRiskAssessments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [compResp, riskResp] = await Promise.all([
        api.get('/compliance/compliance-check/factory-id'),
        api.get('/compliance/risk-assessment/factory-id')
      ]);
      setComplianceChecks(compResp.data.data || []);
      setRiskAssessments(riskResp.data.data || []);
    } catch (error) {
      console.error('Failed to fetch compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevel = (level) => {
    switch (level) {
      case 'critical': return { color: 'red', text: 'Critical' };
      case 'high': return { color: 'orange', text: 'High' };
      case 'medium': return { color: 'yellow', text: 'Medium' };
      default: return { color: 'green', text: 'Low' };
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Compliance & Risk Management</h1>
        <p className="text-gray-600">Monitor compliance status and manage risks</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Compliance Status</h3>
            <Shield className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-3">
            {complianceChecks.slice(0, 5).map((check) => (
              <div key={check.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-gray-500" />
                  <div>
                    <p className="font-medium text-gray-900">{check.regulation}</p>
                    <p className="text-sm text-gray-600">{check.check_type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    check.status === 'compliant' ? 'bg-green-100 text-green-800' :
                    check.status === 'non_compliant' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {check.status}
                  </span>
                  {check.compliance_score && (
                    <span className="text-sm font-medium text-gray-600">
                      {Math.round(check.compliance_score)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Risk Assessments</h3>
            <AlertTriangle className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-3">
            {riskAssessments.slice(0, 5).map((risk) => {
              const level = getRiskLevel(risk.risk_level);
              return (
                <div key={risk.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className={`w-4 h-4 text-${level.color}-500`} />
                    <div>
                      <p className="font-medium text-gray-900">{risk.risk_category}</p>
                      <p className="text-sm text-gray-600">Score: {risk.risk_score}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium bg-${level.color}-100 text-${level.color}-800`}>
                    {level.text}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm text-gray-600">Compliant</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {complianceChecks.filter(c => c.status === 'compliant').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-yellow-600" />
            <span className="text-sm text-gray-600">Pending</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {complianceChecks.filter(c => c.status === 'pending').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="text-sm text-gray-600">Non-Compliant</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {complianceChecks.filter(c => c.status === 'non_compliant').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="w-5 h-5 text-blue-600" />
            <span className="text-sm text-gray-600">Avg Score</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {Math.round(complianceChecks.reduce((acc, c) => acc + (c.compliance_score || 0), 0) / complianceChecks.length || 0)}%
          </p>
        </div>
      </div>
    </div>
  );
}
