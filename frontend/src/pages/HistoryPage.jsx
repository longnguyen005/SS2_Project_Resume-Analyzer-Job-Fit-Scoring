import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Clock3, FileText, Files, Upload } from "lucide-react";
import HistoryRow from "../components/HistoryRow/HistoryRow";
import MetricTile from "../components/MetricTile/MetricTile";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";
import { buildHistoryRowViewModel, calculateAverageScore, formatCvDate } from "../lib/cvReadModels";

export default function HistoryPage() {
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
      setUploads(data);
    } catch (error) {
      handleProtectedPageError(error, "Unable to load upload history.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleProtectedPageError(error, fallbackMessage) {
    if (error.status === 401) {
      logout();
      navigate("/login", { replace: true });
      return;
    }

    setMessage(error.message || fallbackMessage);
  }

  const completedUploads = uploads.filter((item) => item.status === "completed");
  const latestCompletedUpload = completedUploads[0] || null;
  const metrics = [
    {
      icon: <FileText size={18} strokeWidth={2.2} />,
      label: "Total Uploads",
      value: String(uploads.length),
      note: "Resumes stored in your pipeline",
      accent: "blue",
    },
    {
      icon: <Clock3 size={18} strokeWidth={2.2} />,
      label: "Completed",
      value: String(completedUploads.length),
      note: "Analyses ready to review",
      accent: "orange",
    },
    {
      icon: <Files size={18} strokeWidth={2.2} />,
      label: "Average Score",
      value: calculateAverageScore(uploads),
      note: "Across completed resume analyses",
      accent: "purple",
    },
    {
      icon: <Upload size={18} strokeWidth={2.2} />,
      label: "Latest Upload",
      value: uploads[0] ? formatCvDate(uploads[0].created_at) : "-",
      note: uploads[0]?.filename || "No uploads yet",
      accent: "green",
    },
  ];

  return (
    <div className="site-page">
      <TopNav
        actions={[
          { label: "Upload New Resume", to: "/upload", variant: "primary" },
        ]}
        compact
      />
      <main className="section-spacer">
        <div className="shell report-shell">
          <div className="page-intro">
            <h1>Resume History</h1>
            <p>Track your resume improvements and review completed analyses.</p>
          </div>

          <div className="metric-grid">
            {metrics.map((item) => (
              <MetricTile key={item.label} {...item} />
            ))}
          </div>

          <section className="journey-card">
            <h2>Your Progress Journey</h2>
            <p>
              {completedUploads.length > 0
                ? `You have ${completedUploads.length} completed analyses. Latest score: ${latestCompletedUpload?.analysis_summary?.overall_score ?? "-"} / 100.`
                : "Upload a resume to start building your analysis history."}
            </p>
          </section>

          <section className="history-card">
            <div className="section-heading">
              <h2>Analysis History</h2>
            </div>
            <div className="history-table">
              <div className="history-header">
                <span>Resume File</span>
                <span>Upload Date</span>
                <span>Score</span>
                <span>Grade</span>
                <span>Status</span>
                <span>Result</span>
              </div>
              {isLoading ? <p className="page-feedback">Loading...</p> : null}
              {!isLoading && message ? <p className="page-feedback error">{message}</p> : null}
              {!isLoading && !message && uploads.length === 0 ? (
                <div className="empty-state">
                  <strong>No CV uploads yet</strong>
                </div>
              ) : null}
              {uploads.map((item) => (
                <HistoryRow key={item.id} item={buildHistoryRowViewModel(item)} />
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
