import { getCvStatusLabel, isCompletedCvStatus, normalizeCvStatus } from "./cvStatusModel";

export function formatCvDate(value) {
  return new Date(value).toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function formatCvDateTime(value) {
  return new Date(value).toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatFileSize(size) {
  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export function buildHistoryRowViewModel(item) {
  const status = normalizeCvStatus(item.status);
  return {
    id: item.id,
    file: item.filename,
    size: formatFileSize(item.file_size_bytes),
    date: formatCvDate(item.created_at),
    score: item.analysis_summary?.overall_score ?? "-",
    grade: item.analysis_summary?.grade ?? "Pending",
    status,
    statusLabel: getCvStatusLabel(status),
    canViewResult: isCompletedCvStatus(status),
  };
}

export function calculateAverageScore(items) {
  const scoredItems = items.filter((item) => typeof item.analysis_summary?.overall_score === "number");

  if (scoredItems.length === 0) {
    return "-";
  }

  const total = scoredItems.reduce((sum, item) => sum + item.analysis_summary.overall_score, 0);
  return Math.round(total / scoredItems.length).toString();
}

export function normalizeResultData(data) {
  return {
    cv_id: data.cv_id,
    filename: data.filename || "uploaded-resume.pdf",
    analyzed_at: data.analyzed_at,
    analysis_provider: data.analysis_provider || null,
    overall_score: Number(data.overall_score || 0),
    grade: data.grade || "Pending",
    summary: data.summary || "Result summary is not available yet.",
    breakdown: Array.isArray(data.breakdown) ? data.breakdown : [],
    skill_chart: Array.isArray(data.skill_chart) ? data.skill_chart : [],
    content_quality: Array.isArray(data.content_quality) ? data.content_quality : [],
    strengths: Array.isArray(data.strengths) ? data.strengths : [],
    improvements: Array.isArray(data.improvements) ? data.improvements : [],
    suggestions: Array.isArray(data.suggestions) ? data.suggestions : [],
  };
}

export function formatAnalysisProviderLabel(provider) {
  return provider || "Unknown";
}
