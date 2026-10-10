import React from 'react';
import { useLocation } from 'react-router-dom';
import { Users, DollarSign, Clock } from 'lucide-react';
import DashboardHeader from '../components/DashboardHeader';
import MetricCard from '../components/MetricCard';
import UtilizationChart from '../components/UtilizationChart';
import ContextStatementBox from '../components/ContextStatementBox';
import { initialMockReport } from '../data/mockData';

export default function ReportDashboardPage({ reportData }) {
  const location = useLocation();
  const data = location.state || reportData || initialMockReport;

  const {
    highSchoolName = 'Lincoln High School',
    zipCode = '08901',
    utilization = { taken: 3, offered: 5, percentage: 60 },
    metrics = {
      counselorRatio: 500,
      stateAvgCounselorRatio: 250,
      medianIncome: 40000,
      stateAvgIncome: 85000,
      timeDeficit: 20,
    },
    contextStatement = 'The student has demonstrated significant resilience...',
  } = data;

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val);
  };

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto">
      <DashboardHeader
        highSchoolName={highSchoolName}
        zipCode={zipCode}
      />

      {/* Metric Cards: Counselor Ratio, Income, Time Deficit */}
      <section className="mb-8">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
          Environmental Baseline Metrics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <MetricCard
            title="Counselor Ratio"
            value={`${metrics.counselorRatio || 500}:1`}
            baselineValue={`${metrics.stateAvgCounselorRatio || 250}:1`}
            baselineLabel="State Standard"
            icon={Users}
            trend="deficit"
            trendLabel="High Caseload"
            description="Student-to-guidance counselor ratio at applicant's high school."
          />

          <MetricCard
            title="Community Median Income"
            value={formatCurrency(metrics.medianIncome || 40000)}
            baselineValue={formatCurrency(metrics.stateAvgIncome || 85000)}
            baselineLabel="State Average"
            icon={DollarSign}
            trend="deficit"
            trendLabel="Economic Disadvantage"
            description="Median household income estimated by community ZIP / school catchment."
          />

          <MetricCard
            title="Time Deficit / Survival Hours"
            value={`${metrics.timeDeficit || 20} hrs/wk`}
            baselineValue="0 hrs"
            baselineLabel="Ideal Extracurricular Time"
            icon={Clock}
            trend="deficit"
            trendLabel="Restricted Bandwidth"
            description="Non-academic family obligations, work, or elder care limiting study hours."
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

      {/* AI Contextual Statement Box */}
      <section className="mb-8">
        <ContextStatementBox statement={contextStatement} />
      </section>
    </div>
  );
}

