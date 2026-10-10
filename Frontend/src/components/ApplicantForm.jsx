import React, { useState } from 'react';
import { School, MapPin, Award, Clock, ArrowRight, Loader2 } from 'lucide-react';

export default function ApplicantForm({ onSubmit, isLoading }) {
  const [formData, setFormData] = useState({
    highSchoolName: '',
    zipCode: '',
    apsTaken: '',
    survivalHours: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.highSchoolName || !formData.zipCode) {
      alert('Please fill in high school name and zip code.');
      return;
    }

    onSubmit({
      highSchoolName: formData.highSchoolName.trim(),
      zipCode: formData.zipCode.trim(),
      apsTaken: Number(formData.apsTaken) || 0,
      survivalHours: Number(formData.survivalHours) || 0,
    });
  };

  const handleFillSample = () => {
    setFormData({
      highSchoolName: 'Lincoln High School',
      zipCode: '08901',
      apsTaken: '3',
      survivalHours: '20',
    });
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-slate-200/80 p-8 sm:p-10 max-w-xl mx-auto transition-all">
      <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-100">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Student Background Profile</h2>
          <p className="text-sm text-slate-500">Enter applicant environmental data points</p>
        </div>
        <button
          type="button"
          onClick={handleFillSample}
          className="text-xs font-medium text-blue-600 hover:text-blue-800 hover:underline px-2.5 py-1 rounded bg-blue-50 border border-blue-100 transition"
        >
          Fill Demo Data
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="highSchoolName" className="block text-sm font-semibold text-slate-700 mb-2">
            High School Name
          </label>
          <div className="relative rounded-lg shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <School className="w-5 h-5" />
            </div>
            <input
              type="text"
              id="highSchoolName"
              name="highSchoolName"
              value={formData.highSchoolName}
              onChange={handleChange}
              placeholder="e.g. New Brunswick High School"
              required
              className="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-sm transition"
            />
          </div>
        </div>

        <div>
          <label htmlFor="zipCode" className="block text-sm font-semibold text-slate-700 mb-2">
            School / Community ZIP Code
          </label>
          <div className="relative rounded-lg shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <MapPin className="w-5 h-5" />
            </div>
            <input
              type="text"
              id="zipCode"
              name="zipCode"
              value={formData.zipCode}
              onChange={handleChange}
              placeholder="e.g. 08901"
              maxLength={5}
              required
              className="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-sm transition"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="apsTaken" className="block text-sm font-semibold text-slate-700 mb-2">
              AP Courses Taken
            </label>
            <div className="relative rounded-lg shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <Award className="w-5 h-5" />
              </div>
              <input
                type="number"
                id="apsTaken"
                name="apsTaken"
                min="0"
                max="30"
                value={formData.apsTaken}
                onChange={handleChange}
                placeholder="e.g. 3"
                required
                className="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-sm transition"
              />
            </div>
          </div>

          <div>
            <label htmlFor="survivalHours" className="block text-sm font-semibold text-slate-700 mb-2">
              Survival Hours / Wk
            </label>
            <div className="relative rounded-lg shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <Clock className="w-5 h-5" />
              </div>
              <input
                type="number"
                id="survivalHours"
                name="survivalHours"
                min="0"
                max="80"
                value={formData.survivalHours}
                onChange={handleChange}
                placeholder="e.g. 20"
                required
                className="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white text-sm transition"
              />
            </div>
          </div>
        </div>

        <p className="text-xs text-slate-500 italic">
          * Survival hours include required jobs, sibling care, family translation, or elder support.
        </p>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full mt-4 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 px-6 rounded-lg shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 transition duration-150"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Generating Context Report...</span>
            </>
          ) : (
            <>
              <span>Generate Context Report</span>
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}

