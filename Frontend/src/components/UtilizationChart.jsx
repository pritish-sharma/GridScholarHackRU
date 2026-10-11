import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';

export default function UtilizationChart({ taken = 0, offered = null, percentage = null }) {
  const hasOffered = typeof offered === 'number';
  const chartData = hasOffered
    ? [
        { name: 'APs Taken by Student', count: taken, fill: '#2563eb' },
        { name: 'Total APs Offered at School', count: offered, fill: '#94a3b8' },
      ]
    : [];

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Opportunity Utilization Index
          </h3>
          <p className="text-xs text-slate-500">
            Compares courses completed against courses actually offered in applicant's curriculum
          </p>
        </div>
        <div className="text-right">
          {typeof percentage === 'number' ? (
            <div className="text-2xl font-black text-blue-600">{percentage}%</div>
          ) : (
            <div className="text-lg font-bold text-slate-400">Unavailable</div>
          )}
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Opportunity Captured
          </span>
        </div>
      </div>

      {hasOffered ? (
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 40, bottom: 10 }}
            >
              <XAxis
                type="number"
                domain={[0, Math.max(offered, taken) + 2]}
                allowDecimals={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={140}
                tick={{ fontSize: 12, fill: '#475569' }}
              />
              <Tooltip
                formatter={(value) => [`${value} Courses`, 'Count']}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #cbd5e1',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={28}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
          We could not verify how many AP courses this school offers, so the comparison chart is
          hidden rather than guessed. The applicant reported taking <strong>{taken}</strong> AP
          course{taken === 1 ? '' : 's'}.
        </div>
      )}

      <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-sm bg-blue-600 inline-block" />
          <span>Student took <strong>{taken}</strong> APs</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-sm bg-slate-400 inline-block" />
          <span>
            {hasOffered ? (
              <>School offers <strong>{offered}</strong> total APs</>
            ) : (
              'School AP offerings unavailable'
            )}
          </span>
        </div>
      </div>
    </div>
  );
}
