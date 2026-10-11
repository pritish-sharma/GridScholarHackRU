import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import HeroSection from '../components/HeroSection';
import ApplicantForm from '../components/ApplicantForm';
import { fetchContextReport, warmUpServer } from '../lib/api';

export default function InputFormPage({ setReportData }) {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    warmUpServer();
  }, []);

  const handleFormSubmit = async (formData) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const report = await fetchContextReport(formData);
      setReportData(report);
      navigate('/report', { state: report });
    } catch (err) {
      console.error('Submission failed:', err);
      setErrorMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <HeroSection />
      {errorMessage && (
        <div
          role="alert"
          className="mb-6 p-4 rounded-lg bg-red-50 border border-red-300 text-red-800 text-sm font-medium max-w-xl mx-auto"
        >
          {errorMessage}
        </div>
      )}
      <ApplicantForm onSubmit={handleFormSubmit} isLoading={isLoading} />
    </div>
  );
}
