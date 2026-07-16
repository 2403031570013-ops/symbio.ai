import { lazy, Suspense } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import FactoryVerificationPage from './pages/FactoryVerificationPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import MobileVerificationPage from './pages/MobileVerificationPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import AdminLoginPage from './pages/AdminLoginPage';
import HelpCenter from './components/HelpCenter';
import ErrorBoundary from './components/ErrorBoundary';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const MaterialListingPage = lazy(() => import('./pages/MaterialListingPage'));
const AiMatchPage = lazy(() => import('./pages/AiMatchPage'));
const TransactionsPage = lazy(() => import('./pages/TransactionsPage'));
const EsgAnalyticsPage = lazy(() => import('./pages/EsgAnalyticsPage'));
const AdminPanelPage = lazy(() => import('./pages/AdminPanelPage'));
const AIRecommendationsPage = lazy(() => import('./pages/AIRecommendationsPage'));
const ESGDashboardPage = lazy(() => import('./pages/ESGDashboardPage'));
const SupplyChainPage = lazy(() => import('./pages/SupplyChainPage'));
const CompliancePage = lazy(() => import('./pages/CompliancePage'));
const MarketplacePage = lazy(() => import('./pages/MarketplacePage'));

function AppLoader({ label = 'Loading SymbioAI workspace...' }) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4 text-slate-200">
      <div className="w-full max-w-sm rounded-3xl border border-white/10 bg-white/[0.07] p-6 text-center shadow-2xl shadow-slate-950/30 backdrop-blur-xl">
        <div className="mx-auto h-12 w-12 animate-pulse rounded-2xl bg-gradient-to-br from-emerald-300 to-emerald-700 shadow-lg shadow-emerald-950/30" />
        <p className="mt-4 text-sm font-semibold text-white">{label}</p>
        <p className="mt-2 text-xs text-slate-400">Preparing secure enterprise controls</p>
      </div>
    </div>
  );
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, isAuthLoading } = useAuth();
  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.16),_transparent_35%),linear-gradient(135deg,_#031427_0%,_#061b2c_55%,_#020812_100%)]">
        <AppLoader />
      </div>
    );
  }
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AdminRoute({ children }) {
  const { user, isAuthenticated, isAuthLoading } = useAuth();
  if (isAuthLoading) {
    return (
      <AppLoader label="Checking admin permissions..." />
    );
  }
  if (!isAuthenticated) return <Navigate to="/admin/login" replace />;
  return ['Admin', 'Super Admin'].includes(user?.role) ? children : <Navigate to="/dashboard" replace state={{ accessDenied: true }} />;
}

export default function App() {
  return (
    <AuthProvider>
      <ErrorBoundary>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/admin/login" element={<AdminLoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify-factory" element={<FactoryVerificationPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
            <Route path="/verify-mobile" element={<MobileVerificationPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Suspense fallback={<AppLoader />}><DashboardPage /></Suspense>} />
              <Route path="listings" element={<Suspense fallback={<AppLoader />}><MaterialListingPage /></Suspense>} />
              <Route path="sell" element={<Navigate to="/listings" replace />} />
              <Route path="upload" element={<Navigate to="/listings" replace />} />
              <Route path="matches" element={<Suspense fallback={<AppLoader />}><AiMatchPage /></Suspense>} />
              <Route path="ai-match" element={<Navigate to="/matches" replace />} />
              <Route path="chat" element={<Navigate to="/matches" replace />} />
              <Route path="transactions" element={<Suspense fallback={<AppLoader />}><TransactionsPage /></Suspense>} />
              <Route path="orders" element={<Navigate to="/transactions" replace />} />
              <Route path="reports" element={<Navigate to="/esg" replace />} />
              <Route path="esg" element={<Suspense fallback={<AppLoader />}><EsgAnalyticsPage /></Suspense>} />
              <Route path="ai-recommendations" element={<Suspense fallback={<AppLoader />}><AIRecommendationsPage /></Suspense>} />
              <Route path="esg-dashboard" element={<Suspense fallback={<AppLoader />}><ESGDashboardPage /></Suspense>} />
              <Route path="supply-chain" element={<Suspense fallback={<AppLoader />}><SupplyChainPage /></Suspense>} />
              <Route path="compliance" element={<Suspense fallback={<AppLoader />}><CompliancePage /></Suspense>} />
              <Route path="marketplace" element={<Suspense fallback={<AppLoader />}><MarketplacePage /></Suspense>} />
              <Route path="buy" element={<Navigate to="/marketplace" replace />} />
              <Route path="settings" element={<Navigate to="/dashboard" replace />} />
              <Route path="profile" element={<Navigate to="/dashboard" replace />} />
            </Route>
            <Route path="/admin" element={<Suspense fallback={<AppLoader label="Loading Admin Console..." />}><AdminRoute><AdminPanelPage /></AdminRoute></Suspense>} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          <HelpCenter />
        </BrowserRouter>
      </ErrorBoundary>
    </AuthProvider>
  );
}
