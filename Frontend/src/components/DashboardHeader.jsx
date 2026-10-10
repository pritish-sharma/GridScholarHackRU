import React from 'react';
import { Printer, ArrowLeft, Building2, MapPin, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function DashboardHeader({ highSchoolName, zipCode }) {
  const navigate = useNavigate();

  const handlePrint = () => {
    window.print();
  };

  return (
    <header className="mb-8 border-b border-slate-200 pb-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/')}
            className="no-print inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-blue-600 transition mb-3"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Assessment Form
          </button>
          
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              <ShieldCheck className="w-3.5 h-3.5" />
              Verified Baseline
            </span>
            <span className="text-xs text-slate-400">DeltaMetrics Assessment</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Applicant Environmental Context Dossier
          </h1>

          <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-slate-600">
            <span className="inline-flex items-center gap-1.5">
              <Building2 className="w-4 h-4 text-slate-400" />
              <strong className="font-medium text-slate-800">{highSchoolName || 'Lincoln High School'}</strong>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-slate-400" />
              <span>ZIP {zipCode || '08901'}</span>
            </span>
          </div>
        </div>

        <div className="no-print flex items-center gap-3">
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 hover:border-slate-400 text-sm font-semibold shadow-sm transition"
          >
            <Printer className="w-4 h-4 text-slate-600" />
            Print to PDF
          </button>
        </div>
      </div>
    </header>
  );
}

