import React, { useState } from 'react';
import { Sparkles, Copy, Check } from 'lucide-react';

export default function ContextStatementBox({ statement }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!statement) return;
    navigator.clipboard.writeText(statement);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-850 to-indigo-950 text-white rounded-2xl p-6 sm:p-8 shadow-xl border border-slate-700/60 print:bg-white print:text-black print:border-slate-300 print:shadow-none">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-blue-500/20 text-blue-400 border border-blue-400/30 print:hidden">
            <Sparkles className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-semibold tracking-wide uppercase text-blue-300 print:text-slate-700">
            AI-Synthesized Holistic Context Statement
          </h3>
        </div>

        <button
          onClick={handleCopy}
          className="no-print inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
          title="Copy text to clipboard"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      <p className="text-base sm:text-lg leading-relaxed text-slate-100 font-serif italic print:text-slate-900">
        "{statement || 'No context statement available.'}"
      </p>

      <div className="mt-4 pt-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between print:text-slate-600 print:border-slate-200">
        <span>Prepared for Admissions Committee Holistic Review</span>
        <span className="font-mono text-[11px] text-slate-500 print:text-slate-600">DeltaMetrics AI Model</span>
      </div>
    </div>
  );
}

