import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import HeroSection from '../components/HeroSection';
import ApplicantForm from '../components/ApplicantForm';
import { initialMockReport } from '../data/mockData';

export default function InputFormPage({ setReportData }) {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleFormSubmit = async (formData) => {
    setIsLoading(true);

    try {
      const response = await fetch('https://gridscholar.onrender.com/api/context-report', {  
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // STRICT PAYLOAD: Matches FastAPI snake_case requirements exactly
        body: JSON.stringify({
          high_school_name: String(formData.highSchoolName || '').trim(), 
          zip_code: String(formData.zipCode || '').trim(),
          ap_classes_taken: Number(formData.apsTaken || 0),
          survival_hours_per_week: Number(formData.survivalHours || 0)
        })
      });

      if (response.ok) {
        const data = await response.json();
        const fullReport = {
          ...formData,
          ...data,
        };
        setReportData(fullReport);
        navigate('/report', { state: fullReport });
        return;
      }
      
      const errorData = await response.json().catch(() => null);
      console.error("Backend validation error:", errorData);
      throw new Error(`Server returned ${response.status}`);
      
    } catch (err) {
      console.warn('Backend API unavailable or error returned, using dynamic local simulation:', err.message);
      
      // Fallback calculation for demo/mock mode
      const estimatedOffered = Math.max(Number(formData.apsTaken || 0) + 2, 5);
      const computedPercentage = Math.round((Number(formData.apsTaken || 0) / estimatedOffered) * 100);

      const fallbackReport = {
        ...formData,
        utilization: {
          taken: Number(formData.apsTaken || 0),
          offered: estimatedOffered,
          percentage: computedPercentage,
        },
        metrics: {
          counselorRatio: 480,
          stateAvgCounselorRatio: 250,
          medianIncome: 42000,
          stateAvgIncome: 85000,
          timeDeficit: Number(formData.survivalHours || 0),
        },
        contextStatement: `The applicant at ${formData.highSchoolName || 'their high school'} (ZIP ${formData.zipCode || 'community'}) took ${formData.apsTaken} AP courses out of ${estimatedOffered} offered (${computedPercentage}% opportunity utilization). Navigating a high counselor-to-student ratio of 480:1 alongside ${formData.survivalHours} weekly survival hours, this student has achieved superior academic rigor relative to available school and community resources.`,
      };

      setReportData(fallbackReport);
      navigate('/report', { state: fallbackReport });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <HeroSection />
      <ApplicantForm onSubmit={handleFormSubmit} isLoading={isLoading} />
    </div>
  );
}
