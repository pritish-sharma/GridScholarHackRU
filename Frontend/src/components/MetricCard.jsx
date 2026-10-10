import React from 'react';

export default function MetricCard({
  title,
  value,
  baselineValue,
  baselineLabel,
  icon: Icon,
  trend,
  trendLabel,
  description,
}) {
  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm p-5 flex flex-col justify-between hover:shadow-md transition">
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            {title}
          </span>
          {Icon && (
            <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
              <Icon className="w-4 h-4" />
            </div>
          )}
        </div>

        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
            {value}
          </span>
          {trend && (
            <span
              className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                trend === 'deficit'
                  ? 'bg-amber-100 text-amber-800'
                  : trend === 'positive'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-slate-100 text-slate-700'
              }`}
            >
              {trendLabel}
            </span>
          )}
        </div>

        {baselineValue && (
          <div className="text-xs text-slate-500 mb-2">
            <span className="font-medium text-slate-700">State Avg:</span> {baselineValue}
            {baselineLabel && ` (${baselineLabel})`}
          </div>
        )}
      </div>

      {description && (
        <p className="mt-2 text-xs text-slate-500 border-t border-slate-100 pt-2.5">
          {description}
        </p>
      )}
    </div>
  );
}

