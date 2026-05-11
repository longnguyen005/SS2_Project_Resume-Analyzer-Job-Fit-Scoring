import { useEffect, useMemo, useRef, useState } from "react";
import { Link, createSearchParams, useNavigate, useSearchParams } from "react-router-dom";
import BrandLogo from "../components/BrandLogo/BrandLogo";
import LoadingSpinner from "../components/LoadingSpinner";
import ProgressStep from "../components/ProgressStep/ProgressStep";
import { apiRequest } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import {
  buildProcessingStepViews,
  getProcessingLoadingLabel,
  getProcessingProgress,
  getProcessingStatusCopy,
  shouldShowProcessingLoadingState,
} from "../lib/cvProcessingViewModel";

export default function ProcessingPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { logout } = useAuth();
  const [backendStatus, setBackendStatus] = useState("pending");
  const [failureReason, setFailureReason] = useState("");
  const [failedStage, setFailedStage] = useState("");
  const [message, setMessage] = useState("");
  const [isLoadingStatus, setIsLoadingStatus] = useState(true);
  const cvId = searchParams.get("cvId");
  const hasRedirectedRef = useRef(false);

  useEffect(() => {
    if (!cvId) {
      setMessage("No uploaded CV was found. Please return to upload and try again.");
      setIsLoadingStatus(false);
      return undefined;
    }

    let isMounted = true;
    let pollingTimer = null;

    async function loadStatus() {
      try {
        const data = await apiRequest(`/cv/${cvId}/status`);
        if (!isMounted) {
          return;
        }

        setBackendStatus(data.status);
        setFailureReason(data.failure_reason || "");
        setFailedStage(data.failed_stage || "");
        setIsLoadingStatus(false);
        setMessage("");

        if (data.status === "completed") {
          if (!hasRedirectedRef.current) {
            hasRedirectedRef.current = true;
            window.setTimeout(() => {
              navigate({
                pathname: "/result",
                search: createSearchParams({ cvId }).toString(),
              });
            }, 900);
          }
          return;
        }

        if (data.status === "failed") {
          setMessage(data.failure_reason || "Resume processing failed. Please upload the file again or try another CV.");
          return;
        }

        pollingTimer = window.setTimeout(loadStatus, 1500);
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setIsLoadingStatus(false);
        if (error.status === 401) {
          logout();
          navigate("/login", { replace: true });
          return;
        }

        setMessage(error.message || "Unable to retrieve the current analysis status.");
      }
    }

    loadStatus();

    return () => {
      isMounted = false;
      if (pollingTimer) {
        window.clearTimeout(pollingTimer);
      }
    };
  }, [cvId, logout, navigate]);

  const progress = useMemo(() => {
    return getProcessingProgress(backendStatus, failedStage);
  }, [backendStatus, failedStage]);

  const statusCopy = useMemo(() => {
    return getProcessingStatusCopy(backendStatus, failureReason);
  }, [backendStatus, failureReason]);

  const loadingLabel = useMemo(() => {
    return getProcessingLoadingLabel(backendStatus);
  }, [backendStatus]);

  const showLoadingState = shouldShowProcessingLoadingState(isLoadingStatus, backendStatus);

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
          {backendStatus === "failed" ? (
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
