export const homeTrustPills = ["Free to use", "Instant results", "Secure & private"];

export const featureCards = [
  {
    icon: "AI",
    title: "AI Resume Score",
    description: "Get an instant comprehensive score based on industry standards and best practices.",
    accent: "blue",
  },
  {
    icon: "JF",
    title: "Job Fit Analysis",
    description: "Analyze how well your skills and experience match current job market demands.",
    accent: "purple",
  },
  {
    icon: "IP",
    title: "Improvement Tips",
    description: "Receive AI-powered suggestions to enhance your resume and stand out to recruiters.",
    accent: "green",
  },
  {
    icon: "HS",
    title: "History Tracking",
    description: "Track your resume improvements over time with detailed analysis history.",
    accent: "orange",
  },
];

export const processingSteps = [
  {
    icon: "1",
    title: "Extracting resume text",
    description: "Reading and parsing your resume content",
    state: "active",
    badge: "Processing",
  },
  {
    icon: "2",
    title: "Analyzing skills",
    description: "Identifying and evaluating your skills",
    state: "pending",
  },
  {
    icon: "3",
    title: "Calculating job fit score",
    description: "Generating comprehensive analysis",
    state: "pending",
  },
];

export const resultBreakdown = [
  { title: "Skills", score: 92, status: "Excellent", tone: "navy" },
  { title: "Experience", score: 85, status: "Excellent", tone: "navy" },
  { title: "Education", score: 88, status: "Excellent", tone: "navy" },
  { title: "Resume Format", score: 83, status: "Good", tone: "navy" },
];

export const skillChartBars = [
  { label: "Technical", value: 92 },
  { label: "Leadership", value: 78 },
  { label: "Communication", value: 86 },
  { label: "Problem Solving", value: 89 },
];

export const contentQualityLegend = [
  { label: "Strong", value: "65%", tone: "green" },
  { label: "Good", value: "25%", tone: "blue" },
  { label: "Needs Work", value: "10%", tone: "orange" },
];

export const resultStrengths = [
  "Strong technical skill set with modern technologies",
  "Clear and concise professional summary",
  "Well-structured work experience section",
  "Relevant certifications and education",
];

export const areasForImprovement = [
  "Limited quantifiable achievements",
  "Missing some trending industry keywords",
  "Could improve formatting consistency",
];

export const resultSuggestions = [
  {
    title: "Add Quantifiable Achievements",
    description:
      "Include specific metrics and numbers to demonstrate your impact. For example, 'Increased sales by 35%' instead of 'Improved sales'.",
    priority: "High Priority",
    tone: "red",
  },
  {
    title: "Update Skills Section",
    description:
      "Add trending technologies and skills relevant to your industry. Consider adding: Cloud Computing, Machine Learning, or Data Analytics.",
    priority: "Medium Priority",
    tone: "yellow",
  },
  {
    title: "Optimize Formatting",
    description:
      "Use consistent formatting throughout. Ensure all dates follow the same format and bullet points are aligned properly.",
    priority: "Low Priority",
    tone: "blue",
  },
  {
    title: "Enhance Action Verbs",
    description:
      "Start bullet points with strong action verbs like 'Spearheaded', 'Orchestrated', or 'Optimized' instead of 'Responsible for' or 'Worked on'.",
    priority: "Medium Priority",
    tone: "blue",
  },
  {
    title: "Tailor To Job Description",
    description:
      "Customize your resume for each application by including relevant keywords from the job posting.",
    priority: "High Priority",
    tone: "yellow",
  },
];

export const historyMetrics = [
  { icon: "TA", label: "Total Analyses", value: "4", accent: "blue" },
  { icon: "CS", label: "Current Score", value: "87/100", accent: "green" },
  { icon: "UP", label: "Improvement", value: "+19 pts", accent: "purple" },
  { icon: "LU", label: "Last Upload", value: "Today", accent: "orange" },
];

export const progressJourney = [
  { version: "v4", score: 68 },
  { version: "v3", score: 74 },
  { version: "v2", score: 82 },
  { version: "v1", score: 87 },
];

export const historyItems = [
  {
    file: "John_Doe_Resume_v3.pdf",
    size: "552 KB",
    date: "March 16, 2026",
    score: 87,
    grade: "Very Good",
    change: "+5 pts",
    status: "Completed",
  },
  {
    file: "John_Doe_Resume_v2.pdf",
    size: "579 KB",
    date: "March 10, 2026",
    score: 82,
    grade: "Very Good",
    change: "+8 pts",
    status: "Completed",
  },
  {
    file: "John_Doe_Resume_v1.pdf",
    size: "511 KB",
    date: "March 5, 2026",
    score: 74,
    grade: "Good",
    change: "First version",
    status: "Completed",
  },
  {
    file: "Resume_Draft.docx",
    size: "388 KB",
    date: "February 28, 2026",
    score: 68,
    grade: "Fair",
    change: "-6 pts",
    status: "Completed",
  },
];

export const jobDescriptions = [
  {
    id: "jd-1",
    title: "Backend Engineer",
    description: "Python, FastAPI, PostgreSQL, Docker, REST API design, and async services.",
  },
  {
    id: "jd-2",
    title: "AI Engineer",
    description: "Prompt design, LLM integration, evaluation, vector search, and workflow automation.",
  },
  {
    id: "jd-3",
    title: "Product Analyst",
    description: "SQL, analytics dashboards, experiments, and business storytelling.",
  },
];
