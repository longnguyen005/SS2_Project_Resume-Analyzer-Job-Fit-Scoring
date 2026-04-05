import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import HistoryRow from "../components/HistoryRow/HistoryRow";
import MetricTile from "../components/MetricTile/MetricTile";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";
import { FileText, Clock3, Files, Upload } from "lucide-react";

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
      handleProtectedPageError(error, "Không thể tải lịch sử upload.");
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

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  const metrics = [
    {
      icon: <FileText size={18} strokeWidth={2.2} />,
      label: "Total Uploads",
      value: String(uploads.length),
      accent: "blue",
    },
    {
      icon: <Clock3 size={18} strokeWidth={2.2} />,
      label: "Pending",
      value: String(uploads.filter((item) => item.status === "pending").length),
      accent: "orange",
    },
    {
      icon: <Files size={18} strokeWidth={2.2} />,
      label: "File Types",
      value: uploads.length ? Array.from(new Set(uploads.map((item) => item.file_type.toUpperCase()))).join(", ") : "-",
      accent: "purple",
    },
    {
      icon: <Upload size={18} strokeWidth={2.2} />,
      label: "Latest Upload",
      value: uploads[0] ? formatDate(uploads[0].created_at) : "-",
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
            <p>Track your resume improvements and view past analyses</p>
          </div>

          <div className="metric-grid">
            {metrics.map((item) => (
              <MetricTile key={item.label} {...item} />
            ))}
          </div>

          <section className="journey-card">
            <h2>Protected API Status</h2>
          </section>

          <section className="history-card">
            <div className="section-heading">
              <h2>Analysis History</h2>
            </div>
            <div className="history-table">
              <div className="history-header">
                <span>Resume File</span>
                <span>Upload Date</span>
                <span>Type</span>
                <span>Size</span>
                <span>Status</span>
                <span>Linked JD</span>
              </div>
              {isLoading ? <p className="page-feedback">Loading...</p> : null}
              {!isLoading && message ? <p className="page-feedback error">{message}</p> : null}
              {!isLoading && !message && uploads.length === 0 ? (
                <div className="empty-state">
                  <strong>There are no cv upload</strong>
                </div>
              ) : null}
              {uploads.map((item) => (
                <HistoryRow key={item.id} item={mapUploadToHistoryRow(item)} />
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

function formatDate(value) {
  return new Date(value).toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function formatBytes(size) {
  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function mapUploadToHistoryRow(item) {
  return {
    file: item.filename,
    size: formatBytes(item.file_size_bytes),
    date: formatDate(item.created_at),
    type: item.file_type.toUpperCase(),
    linkedJob: item.job_description_id ? "Linked" : "None",
    status: item.status,
  };
}
