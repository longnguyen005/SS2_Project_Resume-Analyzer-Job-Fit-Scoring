import { useEffect, useState } from "react";
import { Link, createSearchParams, useNavigate } from "react-router-dom";
import LoadingSpinner from "../components/LoadingSpinner";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";
import { Upload, Check, Shield, Sparkles } from "lucide-react";

const uploadHighlights = [
  { icon: Check, title: "Instant Analysis", description: "Get results in seconds" },
  { icon: Shield, title: "Secure & Private", description: "Your data is protected" },
  { icon: Sparkles, title: "AI-Powered", description: "Advanced algorithms" },
];

const tips = [
  "Ensure your resume is in PDF or DOCX format",
  "Make sure the text is selectable and not just images",
  "Include all relevant sections: experience, education, skills",
  "Use a clean resume format for better analysis",
];

export default function UploadPage() {
  const { logout } = useAuth();
  const [file, setFile] = useState(null);
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [selectedJobDescriptionId, setSelectedJobDescriptionId] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadJobDescriptions();
  }, []);

  async function loadJobDescriptions() {
    try {
      const items = await apiRequest("/jd");
      setJobDescriptions(items);
    } catch (error) {
      handleProtectedPageError(error, "Unable to load the job description to link with the CV.");
    }
  }

  function handleFileChange(event) {
    const nextFile = event.target.files?.[0] || null;
    setFile(nextFile);
    setMessage("");
  }

  async function handleStartAnalysis() {
    if (!file) {
      setMessageType("error");
      setMessage("Please select a file before uploading.");
      return;
    }

    setIsUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    if (selectedJobDescriptionId) {
      formData.append("job_description_id", selectedJobDescriptionId);
    }

    try {
      const data = await apiRequest("/cv/upload", {
        method: "POST",
        body: formData,
      });

      setMessageType("success");
      setMessage(`Upload successful: ${data.filename}. Redirecting to the processing page...`);
      navigate({
        pathname: "/processing",
        search: createSearchParams({ cvId: data.id }).toString(),
      });
    } catch (error) {
      handleProtectedPageError(error, "Unable to upload CV");
    } finally {
      setIsUploading(false);
    }
  }

  function handleProtectedPageError(error, fallbackMessage) {
    if (error.status === 401) {
      logout();
      navigate("/login", { replace: true });
      return;
    }

    setMessageType("error");
    setMessage(error.message || fallbackMessage);
  }

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  return (
    <div className="site-page">
      <TopNav
        actions={[
          { label: "Back to Home", to: "/", variant: "ghost" },
          { label: "History", to: "/history", variant: "secondary" },
        ]}
        compact
      />
      <main className="section-spacer">
        <div className="shell narrow-shell upload-shell">
          <div className="page-intro center">
            <h1>Upload Your Resume</h1>
            <p>Upload your resume to get instant AI-powered analysis and feedback</p>
          </div>

          <section className="upload-card">
            <label className="dropzone">
              <input type="file" accept=".pdf,.docx" onChange={handleFileChange} />
              <span className="dropzone-icon">
                <Upload size={18} strokeWidth={2.2} />
              </span>
              <h2>Drag and drop your resume here</h2>
              <p>or click to browse files</p>
              <span className="nav-button primary small">Browse Files</span>
              <small>Supported formats: PDF, DOCX (Max 10MB)</small>
              {file ? <strong className="selected-file">Selected file: {file.name}</strong> : null}
            </label>

            <label className="auth-field">
              <span>Link to Job Description (optional)</span>
              <select value={selectedJobDescriptionId} onChange={(event) => setSelectedJobDescriptionId(event.target.value)}>
                <option value="">No linked job description</option>
                {jobDescriptions.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.title}
                  </option>
                ))}
              </select>
            </label>

            <div className="upload-highlight-grid">
              {uploadHighlights.map((item) => {
                const Icon = item.icon;

                return (
                  <article key={item.title} className="upload-highlight">
                    <span className="feature-icon blue">
                      <Icon size={18} strokeWidth={2.2} />
                    </span>
                    <div className="feature-text">
                      <strong>{item.title}</strong>
                      <small>{item.description}</small>
                    </div>
                  </article>
                );
              })}
            </div>

            <div className="upload-actions">
              <button
                type="button"
                className="nav-button primary large upload-primary-action"
                onClick={handleStartAnalysis}
                disabled={isUploading}
              >
                {isUploading ? (
                  <>
                    <LoadingSpinner inline size={16} label="" />
                    Uploading...
                  </>
                ) : (
                  "Start Analysis"
                )}
              </button>
              <Link className="nav-button secondary large upload-secondary-action" to="/job-descriptions">
                Manage Job Descriptions
              </Link>
            </div>
            {message ? <p className={`page-feedback ${messageType}`}>{message}</p> : null}
          </section>

          <section className="tips-card">
            <h3>Tips for best results:</h3>
            <ul>
              {tips.map((tip) => (
                <li key={tip}>{tip}</li>
              ))}
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}
