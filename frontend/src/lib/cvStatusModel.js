export const CV_STATUSES = Object.freeze({
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  FAILED: "failed",
});

export const CV_TERMINAL_STATUSES = new Set([CV_STATUSES.COMPLETED, CV_STATUSES.FAILED]);

export function normalizeCvStatus(status) {
  const normalized = String(status || "").toLowerCase();
  if (Object.values(CV_STATUSES).includes(normalized)) {
    return normalized;
  }
  return CV_STATUSES.PENDING;
}

export function isPendingCvStatus(status) {
  return normalizeCvStatus(status) === CV_STATUSES.PENDING;
}

export function isProcessingCvStatus(status) {
  return normalizeCvStatus(status) === CV_STATUSES.PROCESSING;
}

export function isCompletedCvStatus(status) {
  return normalizeCvStatus(status) === CV_STATUSES.COMPLETED;
}

export function isFailedCvStatus(status) {
  return normalizeCvStatus(status) === CV_STATUSES.FAILED;
}

export function isTerminalCvStatus(status) {
  return CV_TERMINAL_STATUSES.has(normalizeCvStatus(status));
}

export function getCvStatusLabel(status) {
  const normalized = normalizeCvStatus(status);
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

export function getCvStatusClassName(status) {
  const normalized = normalizeCvStatus(status);
  if (isCompletedCvStatus(normalized)) {
    return " completed";
  }
  if (isFailedCvStatus(normalized)) {
    return " failed";
  }
  return "";
}

export function normalizeCvStatusPayload(data) {
  return {
    id: data?.id || null,
    status: normalizeCvStatus(data?.status),
    failureReason: data?.failure_reason || "",
    failedStage: data?.failed_stage || "",
    updatedAt: data?.updated_at || null,
  };
}
