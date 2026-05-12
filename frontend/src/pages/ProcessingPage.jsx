import { useCallback, useEffect, useMemo, useRef } from "react";
import { Link, createSearchParams, useNavigate, useSearchParams } from "react-router-dom";
import BrandLogo from "../components/BrandLogo/BrandLogo";
import LoadingSpinner from "../components/LoadingSpinner";
import ProgressStep from "../components/ProgressStep/ProgressStep";
import { useAuth } from "../context/AuthContext";
import {
  buildProcessingStepViews,
  getProcessingLoadingLabel,
  getProcessingProgress,
  getProcessingStatusCopy,
  shouldShowProcessingLoadingState,
} from "../lib/cvProcessingViewModel";
import { isCompletedCvStatus, isFailedCvStatus } from "../lib/cvStatusModel";
import { useCvStatusPolling } from "../lib/useCvStatusPolling";

export default function ProcessingPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { logout } = useAuth();
  const cvId = searchParams.get("cvId");
  const hasRedirectedRef = useRef(false);
  const handleUnauthorized = useCallback(() => {
    logout();
    navigate("/login", { replace: true });
  }, [logout, navigate]);
  const statusState = useCvStatusPolling(cvId, {
    enabled: Boolean(cvId),
    onUnauthorized: handleUnauthorized,
  });
  const backendStatus = statusState.status;
  const failureReason = statusState.failureReason;
  const failedStage = statusState.failedStage;

  useEffect(() => {
    if (!cvId) {
      return;
    }

    if (!isCompletedCvStatus(backendStatus) || hasRedirectedRef.current) {
      return;
    }

    hasRedirectedRef.current = true;
    const redirectTimer = window.setTimeout(() => {
      navigate({
        pathname: "/result",
        search: createSearchParams({ cvId }).toString(),
      });
    }, 900);

    return () => window.clearTimeout(redirectTimer);
  }, [backendStatus, cvId, navigate]);

  const message = useMemo(() => {
    if (!cvId) {
      return "No uploaded CV was found. Please return to upload and try again.";
    }
    if (isFailedCvStatus(backendStatus)) {
      return failureReason || "Resume processing failed. Please upload the file again or try another CV.";
    }
    return statusState.message;
  }, [backendStatus, cvId, failureReason, statusState.message]);

  const progress = useMemo(() => {
    return getProcessingProgress(backendStatus, failedStage);
  }, [backendStatus, failedStage]);

  const statusCopy = useMemo(() => {
    return getProcessingStatusCopy(backendStatus, failureReason);
  }, [backendStatus, failureReason]);

  const loadingLabel = useMemo(() => {
    return getProcessingLoadingLabel(backendStatus);
  }, [backendStatus]);

  const showLoadingState = shouldShowProcessingLoadingState(statusState.isLoading, backendStatus);

  const stepViews = useMemo(
    () => buildProcessingStepViews(backendStatus, failedStage),
    [backendStatus, failedStage],
  );

  return (
    <div className="processing-page">
      <div className="processing-shell">
        <BrandLogo />
        <section className="processing-card">
          <span className="processing-badge">AI</span>
          <h1>Analyzing Your Resume</h1>
          <p>{statusCopy}</p>
          {showLoadingState ? (
            <div className="processing-live-state" aria-live="polite">
              <LoadingSpinner inline label={loadingLabel} size={18} />
            </div>
          ) : null}
          <div className="overall-progress">
            <div className="panel-header">
              <strong>Overall Progress</strong>
              <span>{progress}%</span>
            </div>
            <div className="score-bar">
              <span className="score-fill blue" style={{ width: `${progress}%` }} />
            </div>
          </div>
          <div className="progress-list">
            {stepViews.map((step) => (
              <ProgressStep key={step.title} {...step} />
            ))}
          </div>
          <div className="processing-note">This usually takes 10-15 seconds. Please don't close this window.</div>
          {message ? <p className="page-feedback error">{message}</p> : null}
          {isFailedCvStatus(backendStatus) ? (
            <div className="hero-actions center-actions" style={{ marginTop: "1rem" }}>
              <Link className="nav-button primary" to="/upload">Upload Again</Link>
              <Link className="nav-button outline" to="/history">View History</Link>
            </div>
          ) : null}
        </section>
        <p className="tiny-note">
          <span className="spark">!</span> Did you know? Recruiters spend an average of 6 seconds reviewing a resume.
        </p>
        <Link className="back-link center-link" to="/upload">
          Return to Upload
        </Link>
      </div>
    </div>
  );
}
