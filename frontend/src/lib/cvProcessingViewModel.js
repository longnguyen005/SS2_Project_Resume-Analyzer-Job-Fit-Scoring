import {
  isCompletedCvStatus,
  isFailedCvStatus,
  isPendingCvStatus,
  isProcessingCvStatus,
  normalizeCvStatus,
} from "./cvStatusModel";

export const CV_PROCESSING_STEPS = [
  {
    icon: "1",
    title: "Extracting resume text",
    description: "Reading and parsing your resume content",
  },
  {
    icon: "2",
    title: "Analyzing skills",
    description: "Identifying and evaluating your skills",
  },
  {
    icon: "3",
    title: "Calculating job fit score",
    description: "Generating comprehensive analysis",
  },
];

const FAILED_STAGE_TO_STEP_INDEX = {
  orchestration: 0,
  extract: 0,
  analyze: 1,
  complete: 2,
};

function getFailedStepIndex(failedStage) {
  return FAILED_STAGE_TO_STEP_INDEX[failedStage] ?? 0;
}

export function getProcessingProgress(status, failedStage) {
  const normalizedStatus = normalizeCvStatus(status);
  const failedStepIndex = getFailedStepIndex(failedStage);

  if (isCompletedCvStatus(normalizedStatus)) {
    return 100;
  }
  if (isProcessingCvStatus(normalizedStatus)) {
    return 68;
  }
  if (isFailedCvStatus(normalizedStatus)) {
    return [34, 68, 100][failedStepIndex] || 34;
  }
  return 25;
}

export function getProcessingStatusCopy(status, failureReason) {
  const normalizedStatus = normalizeCvStatus(status);
  if (isCompletedCvStatus(normalizedStatus)) {
    return "Analysis completed. Redirecting to your result...";
  }
  if (isProcessingCvStatus(normalizedStatus)) {
    return "The resume text has been extracted. We are generating your analysis now.";
  }
  if (isFailedCvStatus(normalizedStatus)) {
    return failureReason || "Processing stopped before the final report could be generated.";
  }
  return "Your upload was received. We are preparing the resume for analysis.";
}

export function getProcessingLoadingLabel(status) {
  const normalizedStatus = normalizeCvStatus(status);
  if (isCompletedCvStatus(normalizedStatus)) {
    return "Finalizing your report and opening the results page...";
  }
  if (isProcessingCvStatus(normalizedStatus)) {
    return "AI analysis is running. This can take a few more seconds.";
  }
  if (isFailedCvStatus(normalizedStatus)) {
    return "";
  }
  return "Upload received. We are validating and preparing your file now.";
}

export function shouldShowProcessingLoadingState(isLoadingStatus, status) {
  return (
    isLoadingStatus
    || isPendingCvStatus(status)
    || isProcessingCvStatus(status)
    || isCompletedCvStatus(status)
  );
}

export function buildProcessingStepViews(status, failedStage) {
  const normalizedStatus = normalizeCvStatus(status);
  const failedStepIndex = getFailedStepIndex(failedStage);

  if (isCompletedCvStatus(normalizedStatus)) {
    return CV_PROCESSING_STEPS.map((step) => ({ ...step, state: "completed", badge: "Completed" }));
  }

  if (isProcessingCvStatus(normalizedStatus)) {
    return CV_PROCESSING_STEPS.map((step, index) => {
      if (index === 0) {
        return { ...step, state: "completed", badge: "Completed" };
      }
      if (index === 1) {
        return { ...step, state: "active", badge: "Processing" };
      }
      return { ...step, state: "pending", badge: "Waiting" };
    });
  }

  if (isFailedCvStatus(normalizedStatus)) {
    return CV_PROCESSING_STEPS.map((step, index) => {
      if (index < failedStepIndex) {
        return { ...step, state: "completed", badge: "Completed" };
      }
      if (index === failedStepIndex) {
        return { ...step, state: "failed", badge: "Failed" };
      }
      return { ...step, state: "pending", badge: "Waiting" };
    });
  }

  return CV_PROCESSING_STEPS.map((step, index) => {
    if (index === 0) {
      return { ...step, state: "active", badge: "Processing" };
    }
    return { ...step, state: "pending", badge: "Waiting" };
  });
}
