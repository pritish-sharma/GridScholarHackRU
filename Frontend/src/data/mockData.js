// Mock data matching the shared API contract (POST /api/context-report response)
export const initialMockReport = {
  highSchoolName: "Lincoln High School",
  zipCode: "08901",
  apsTaken: 3,
  survivalHours: 20,
  utilization: {
    taken: 3,
    offered: 5,
    percentage: 60,
  },
  metrics: {
    counselorRatio: 500,
    stateAvgCounselorRatio: 250,
    medianIncome: 40000,
    stateAvgIncome: 85000,
    timeDeficit: 20,
  },
  contextStatement:
    "The student has demonstrated significant resilience and academic drive by completing 3 out of 5 AP courses available at their school (60% opportunity utilization) while balancing 20 hours per week of survival responsibilities. Given a student-to-counselor ratio of 500:1 (double the state baseline of 250:1) and a community median income of $40,000 versus the state average of $85,000, this student's accomplishments represent exceptional performance within a constrained educational environment.",
};

