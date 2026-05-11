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
  const failedStepIndex = getFailedStepIndex(failedStage);

  if (status === "completed") {
    return 100;
  }
  if (status === "processing") {
    return 68;
  }
  if (status === "failed") {
    return [34, 68, 100][failedStepIndex] || 34;
  }
  return 25;
}

export function getProcessingStatusCopy(status, failureReason) {
  if (status === "completed") {
    return "Analysis completed. Redirecting to your result...";
  }
  if (status === "processing") {
    return "The resume text has been extracted. We are generating your analysis now.";
  }
  if (status === "failed") {
    return failureReason || "Processing stopped before the final report could be generated.";
  }
  return "Your upload was received. We are preparing the resume for analysis.";
}

export function getProcessingLoadingLabel(status) {
  if (status === "completed") {
    return "Finalizing your report and opening the results page...";
  }
  if (status === "processing") {
    return "AI analysis is running. This can take a few more seconds.";
  }
  if (status === "failed") {
    return "";
  }
  return "Upload received. We are validating and preparing your file now.";
}

export function shouldShowProcessingLoadingState(isLoadingStatus, status) {
  return isLoadingStatus || status === "pending" || status === "processing" || status === "completed";
}

export function buildProcessingStepViews(status, failedStage) {
  const failedStepIndex = getFailedStepIndex(failedStage);

  if (status === "completed") {
    return CV_PROCESSING_STEPS.map((step) => ({ ...step, state: "completed", badge: "Completed" }));
  }

  if (status === "processing") {
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

  if (status === "failed") {
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
