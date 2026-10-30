import { HashRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './stores/theme';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CorrelationsPage from './pages/CorrelationsPage';
import PairPage from './pages/PairPage';
import AnomaliesPage from './pages/AnomaliesPage';
import StrategiesPage from './pages/StrategiesPage';
import AlertsPage from './pages/AlertsPage';
import ReportsPage from './pages/ReportsPage';

export default function App() {
  return (
    <ThemeProvider>
      <HashRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/correlations" element={<CorrelationsPage />} />
            <Route path="/pair/:a/:b" element={<PairPage />} />
            <Route path="/anomalies" element={<AnomaliesPage />} />
            <Route path="/strategies" element={<StrategiesPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/reports" element={<ReportsPage />} />
          </Route>
        </Routes>
      </HashRouter>
    </ThemeProvider>
  );
}
