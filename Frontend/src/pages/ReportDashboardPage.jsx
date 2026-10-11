import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Users, DollarSign, Clock } from 'lucide-react';
import DashboardHeader from '../components/DashboardHeader';
import MetricCard from '../components/MetricCard';
import UtilizationChart from '../components/UtilizationChart';
import ContextStatementBox from '../components/ContextStatementBox';
import { DataNotesBanner, SourcesPanel } from '../components/DataNotes';

const formatCurrency = (val) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(val);

// Compare a value with its baseline: more than 10% away counts as above/below.
function compare(value, baseline) {
  if (typeof value !== 'number' || typeof baseline !== 'number' || baseline === 0) return null;
  const ratio = value / baseline;
  if (ratio > 1.1) return 'above';
  if (ratio < 0.9) return 'below';
  return 'near';
}

function EmptyState() {
  return (
    <div className="py-24 px-4 max-w-xl mx-auto text-center">
      <h1 className="text-2xl font-bold text-slate-900">No report yet</h1>
      <p className="mt-2 text-slate-600">
        Enter a student's school details to generate a contextual admissions report.
      </p>
      <Link
        to="/"
        className="mt-6 inline-block rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 transition"
      >
        Start a new report
      </Link>
    </div>
  );
}

export default function ReportDashboardPage({ reportData }) {
  const location = useLocation();
  const data = location.state || reportData;

  if (!data || !data.metrics || !data.utilization) return <EmptyState />;

  const { school = {}, utilization, metrics } = data;

  const counselorCompare = compare(metrics.counselorRatio, metrics.baselineCounselorRatio);
  const incomeCompare = compare(metrics.medianIncome, metrics.baselineIncome);

  const counselorTrend = {
    above: ['deficit', 'Above baseline caseload'],
    below: ['positive', 'Below baseline caseload'],
    near: ['neutral', 'Near baseline'],
  }[counselorCompare];

  const incomeTrend = {
    below: ['deficit', 'Below baseline'],
    above: ['positive', 'Above baseline'],
    near: ['neutral', 'Near baseline'],
  }[incomeCompare];

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto">
      <DashboardHeader
        highSchoolName={school.name || data.highSchoolName}
        enteredName={data.enteredSchoolName}
        zipCode={data.zipCode}
        city={school.city}
        state={school.state}
        verification={school.verification}
        dataYear={school.dataYear}
      />

      <DataNotesBanner notes={data.dataNotes} verification={school.verification} />

      {/* Metric Cards: Counselor Ratio, Income, Time Deficit */}
      <section className="mb-8">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
          Environmental Baseline Metrics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <MetricCard
            title="Counselor Ratio"
            value={metrics.counselorRatio === null ? null : `${metrics.counselorRatio}:1`}
            baselineValue={
              metrics.baselineCounselorRatio === null ? null : `${metrics.baselineCounselorRatio}:1`
            }
            baselineLabel={metrics.baselineCounselorLabel}
            icon={Users}
            trend={counselorTrend?.[0]}
            trendLabel={counselorTrend?.[1]}
            description={`Students per counselor at the applicant's high school.${
              metrics.recommendedCounselorRatio
                ? ` The American School Counselor Association recommends ${metrics.recommendedCounselorRatio}:1.`
                : ''
            }`}
          />

          <MetricCard
            title="Community Median Income"
            value={metrics.medianIncome === null ? null : formatCurrency(metrics.medianIncome)}
            baselineValue={
              metrics.baselineIncome === null ? null : formatCurrency(metrics.baselineIncome)
            }
            baselineLabel={metrics.baselineIncomeLabel}
            icon={DollarSign}
            trend={incomeTrend?.[0]}
            trendLabel={incomeTrend?.[1]}
            description={`Median household income for ZIP ${data.zipCode}${
              metrics.incomeYear ? ` (Census ACS 5-year, ${metrics.incomeYear})` : ''
            }.`}
          />

          <MetricCard
            title="Time Deficit / Survival Hours"
            value={`${metrics.timeDeficit} hrs/wk`}
            baselineValue="0 hrs/wk"
            baselineLabel="no required obligations"
            icon={Clock}
            trend={metrics.timeDeficit > 0 ? 'deficit' : 'neutral'}
            trendLabel={metrics.timeDeficit > 0 ? 'Time committed' : 'None reported'}
            description="Non-academic family obligations, work, or elder care reported by the applicant."
          />
        </div>
      </section>

      {/* Opportunity Utilization Visualizer */}
      <section className="mb-8">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
          Curricular Opportunity
        </h2>
        <UtilizationChart
          taken={utilization.taken}
          offered={utilization.offered}
          percentage={utilization.percentage}
        />
      </section>

      {/* Contextual Statement Box */}
      <section className="mb-8">
        <ContextStatementBox statement={data.contextStatement} source={data.statementSource} />
      </section>

      <SourcesPanel
        sources={data.sources}
        notes={data.dataNotes}
        verification={school.verification}
        schoolNotes={school.notes}
      />
    </div>
  );
}
