import React from 'react';

export default function HeroSection() {
  return (
    <div className="text-center max-w-2xl mx-auto mb-10">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold uppercase tracking-wider mb-4">
        DeltaMetrics Engine
      </div>
      <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
        Contextual Admissions Report
      </h1>
      <p className="mt-4 text-lg text-slate-600 leading-relaxed">
        Evaluating student achievement relative to opportunity. By contrasting AP course access, school resources, and survival hours against state baselines, DeltaMetrics surfaces true student resilience.
      </p>
    </div>
  );
}

