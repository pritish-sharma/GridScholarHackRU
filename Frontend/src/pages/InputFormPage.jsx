import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import HeroSection from '../components/HeroSection';
import ApplicantForm from '../components/ApplicantForm';

export default function InputFormPage({ setReportData }) {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const navigate = useNavigate();

  const handleFormSubmit = async (formData) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch('https://gridscholar.onrender.com/api/context-report', {  
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          high_school_name: String(formData.highSchoolName || '').trim(), 
          zip_code: String(formData.zipCode || '').trim(),
          ap_classes_taken: Number(formData.apsTaken || 0),
          survival_hours_per_week: Number(formData.survivalHours || 0)
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = errorData?.detail || `Server returned status ${response.status}`;
        throw new Error(detail);
      }

      const result = await response.json();
      const payload = result.data || result;

      // Map Gemini's live research to the exact keys your Report UI charts expect
      const formattedReport = {
        ...formData,
        highSchoolName: formData.highSchoolName,
        zipCode: formData.zipCode,
        apsTaken: Number(formData.apsTaken || 0),
        survivalHours: Number(formData.survivalHours || 0),

        utilization: {
          taken: Number(payload?.opportunity_utilization?.ap_classes_taken ?? formData.apsTaken ?? 0),
          offered: Number(payload?.opportunity_utilization?.ap_classes_offered ?? 10),
          percentage: Number(payload?.opportunity_utilization?.percentage ?? 0),
        },
        metrics: {
          counselorRatio: Number(payload?.environmental_baselines?.counselor_ratio ?? 350),
          stateAvgCounselorRatio: Number(payload?.environmental_baselines?.state_avg_counselor_ratio ?? 250),
          medianIncome: Number(payload?.environmental_baselines?.median_income ?? 75000),
          stateAvgIncome: Number(payload?.environmental_baselines?.state_avg_income ?? 85000),
          timeDeficit: Number(payload?.environmental_baselines?.time_deficit ?? formData.survivalHours ?? 0),
        },
        contextStatement: payload?.gemini_context_statement || payload?.context_statement || "No statement generated.",

        // Preserve raw backend payload for compatibility
        rawBackendData: result
      };

      setReportData(formattedReport);
      navigate('/report', { state: formattedReport });

    } catch (err) {
      console.error("Submission failed:", err);
      setErrorMessage(`Failed to generate report: ${err.message}. Check your Render logs if this persists.`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <HeroSection />
      {errorMessage && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-300 text-red-800 text-sm font-medium">
          {errorMessage}
        </div>
      )}
      <ApplicantForm onSubmit={handleFormSubmit} isLoading={isLoading} />
    </div>
  );
}
