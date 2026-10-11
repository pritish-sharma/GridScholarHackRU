import React, { useCallback, useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { Compass } from 'lucide-react';
import InputFormPage from './pages/InputFormPage';
import ReportDashboardPage from './pages/ReportDashboardPage';

const STORAGE_KEY = 'deltametrics:lastReport';

// Keep the last report so refreshing /report (or using the "Live Report" link) still works.
function loadSavedReport() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveReport(report) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(report));
  } catch {
    /* storage unavailable (private mode, etc.): the report still shows this session */
  }
}

export default function App() {
  const [reportData, setReportDataState] = useState(loadSavedReport);

  const setReportData = useCallback((report) => {
    setReportDataState(report);
    saveReport(report);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Navigation Bar */}
      <nav className="no-print bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 font-bold text-lg text-slate-900 hover:opacity-90 transition">
            <div className="p-1.5 rounded-lg bg-blue-600 text-white shadow-sm">
              <Compass className="w-5 h-5" />
            </div>
            <span>Delta<span className="text-blue-600">Metrics</span></span>
          </Link>

          <div className="flex items-center gap-4 text-sm font-medium">
            <Link to="/" className="text-slate-600 hover:text-blue-600 transition">
              New Input
            </Link>
            <Link to="/report" className="text-slate-600 hover:text-blue-600 transition">
              Live Report
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content View with Routes */}
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<InputFormPage setReportData={setReportData} />} />
          <Route path="/report" element={<ReportDashboardPage reportData={reportData} />} />
          <Route path="*" element={<ReportDashboardPage reportData={null} />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="no-print border-t border-slate-200 py-6 text-center text-xs text-slate-400 bg-white">
        DeltaMetrics &bull; HackRU Hackathon Project &bull; Holistic Context Evaluation
      </footer>
    </div>
  );
}
