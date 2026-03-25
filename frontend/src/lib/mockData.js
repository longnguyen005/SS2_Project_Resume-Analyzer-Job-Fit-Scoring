export const summaryCards = [
  { label: "Uploads", value: "14", hint: "3 pending" },
  { label: "Average Score", value: "78", hint: "Across last 5 analyses" },
  { label: "Saved JDs", value: "6", hint: "Reusable role targets" },
];

export const jobDescriptions = [
  { id: "jd-1", title: "Backend Engineer", description: "Python, FastAPI, PostgreSQL, Docker" },
  { id: "jd-2", title: "AI Engineer", description: "LLM integration, NLP, prompt design" },
];

export const uploadQueue = [
  { id: "cv-1", filename: "nguyen-anh-backend.pdf", status: "completed", createdAt: "2026-03-24 10:10" },
  { id: "cv-2", filename: "nguyen-anh-ai.docx", status: "pending", createdAt: "2026-03-24 11:40" },
];

export const resultBreakdown = [
  { category: "Skills", score: 82, feedback: "Good Python backend coverage but cloud exposure is still light." },
  { category: "Experience", score: 76, feedback: "Work history is solid, but impact metrics can be stronger." },
  { category: "Education", score: 80, feedback: "Education is clear and relevant." },
  { category: "Format", score: 72, feedback: "Readable overall, but hierarchy and spacing need cleanup." },
];

export const suggestions = [
  "Add quantified achievements to the two most recent roles.",
  "Group skills by backend, cloud, data, and AI tools.",
  "Tailor the summary section to the selected job description.",
];
