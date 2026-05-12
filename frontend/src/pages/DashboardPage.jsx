import { useEffect, useMemo, useState } from "react";
import { Link, createSearchParams, useNavigate } from "react-router-dom";
import { AlertCircle, Clock3, FileText, Gauge, Upload } from "lucide-react";
import HistoryRow from "../components/HistoryRow/HistoryRow";
import LoadingSpinner from "../components/LoadingSpinner";
import MetricTile from "../components/MetricTile/MetricTile";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";
import { buildHistoryRowViewModel, calculateAverageScore, formatCvDate } from "../lib/cvReadModels";
import { isCompletedCvStatus, isFailedCvStatus } from "../lib/cvStatusModel";

export default function DashboardPage() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [uploads, setUploads] = useState([]);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadUploads();
  }, []);

  async function loadUploads() {
    setIsLoading(true);
    setMessage("");

    try {
      const data = await apiRequest("/cv");
      setUploads(Array.isArray(data) ? data : []);
    } catch (error) {
      if (error.status === 401) {
        logout();
        navigate("/login", { replace: true });
        return;
      }

      setMessage(error.message || "Unable to load dashboard data.");
    } finally {
      setIsLoading(false);
    }
  }

  const completedUploads = useMemo(() => uploads.filter((item) => isCompletedCvStatus(item.status)), [uploads]);
  const failedUploads = useMemo(() => uploads.filter((item) => isFailedCvStatus(item.status)), [uploads]);
  const latestUpload = uploads[0] || null;
  const recentUploads = uploads.slice(0, 5);

  const metrics = [
    {
      icon: <FileText size={18} strokeWidth={2.2} />,
      label: "Total Uploads",
      value: String(uploads.length),
      note: "Resumes in the analysis pipeline",
      accent: "blue",
    },
    {
      icon: <Gauge size={18} strokeWidth={2.2} />,
      label: "Average Score",
      value: calculateAverageScore(uploads),
      note: "Across completed analyses",
      accent: "purple",
    },
    {
      icon: <Clock3 size={18} strokeWidth={2.2} />,
      label: "Completed",
      value: String(completedUploads.length),
      note: "Reports ready to review",
      accent: "green",
    },
    {
      icon: <AlertCircle size={18} strokeWidth={2.2} />,
      label: "Failed",
      value: String(failedUploads.length),
      note: "Uploads that need another attempt",
      accent: "orange",
    },
  ];

  return (
    <div className="site-page">
      <TopNav
        actions={[
          { label: "History", to: "/history", variant: "ghost" },
          { label: "Upload Resume", to: "/upload", variant: "primary" },
        ]}
        compact
      />
      <main className="section-spacer">
        <div className="shell report-shell">
          <div className="page-intro">
            <h1>Dashboard</h1>
            <p>
              {latestUpload
                ? `Latest upload: ${latestUpload.filename} on ${formatCvDate(latestUpload.created_at)}.`
                : "Upload a resume to start tracking your analysis pipeline."}
            </p>
          </div>

          <div className="metric-grid">
            {metrics.map((item) => (
              <MetricTile key={item.label} {...item} />
            ))}
          </div>

          <section className="history-card">
            <div className="section-heading">
              <h2>Recent Uploads</h2>
            </div>

            {isLoading ? (
              <div className="processing-live-state" aria-live="polite">
                <LoadingSpinner inline label="Loading dashboard data..." size={18} />
              </div>
            ) : null}

            {!isLoading && message ? (
              <div className="empty-state">
                <strong>{message}</strong>
                <div className="hero-actions">
                  <button type="button" className="nav-button secondary" onClick={loadUploads}>
                    Retry
                  </button>
                  <Link className="nav-button primary" to="/upload">
                    Upload Resume
                  </Link>
                </div>
              </div>
            ) : null}

            {!isLoading && !message && recentUploads.length === 0 ? (
              <div className="empty-state">
                <strong>No CV uploads yet</strong>
                <p>Your dashboard will populate after your first upload.</p>
                <Link className="nav-button primary" to="/upload">
                  <Upload size={16} strokeWidth={2.2} />
                  Upload Resume
                </Link>
              </div>
            ) : null}

            {!isLoading && !message && recentUploads.length > 0 ? (
              <div className="history-table">
                <div className="history-header">
                  <span>Resume File</span>
                  <span>Upload Date</span>
                  <span>Score</span>
                  <span>Grade</span>
                  <span>Status</span>
                  <span>Result</span>
                </div>
                {recentUploads.map((item) => (
                  <HistoryRow key={item.id} item={buildHistoryRowViewModel(item)} />
                ))}
              </div>
            ) : null}

            {!isLoading && !message && recentUploads.length > 0 ? (
              <div className="hero-actions" style={{ marginTop: "1rem" }}>
                <Link className="nav-button secondary" to="/history">
                  View Full History
                </Link>
                {latestUpload && !isCompletedCvStatus(latestUpload.status) ? (
                  <Link
                    className="nav-button outline"
                    to={`/processing?${createSearchParams({ cvId: latestUpload.id }).toString()}`}
                  >
                    Open Processing
                  </Link>
                ) : null}
              </div>
            ) : null}
          </section>
        </div>
      </main>
    </div>
  );
}
