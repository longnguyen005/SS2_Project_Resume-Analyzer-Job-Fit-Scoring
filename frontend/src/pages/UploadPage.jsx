import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import TopNav from "../components/TopNav/TopNav";

const uploadHighlights = [
  { icon: "IN", title: "Instant Analysis", description: "Get results in seconds" },
  { icon: "SP", title: "Secure & Private", description: "Your data is protected" },
  { icon: "AI", title: "AI-Powered", description: "Advanced algorithms" },
];

const tips = [
  "Ensure your resume is in PDF or DOCX format",
  "Make sure the text is selectable and not just images",
  "Include all relevant sections: experience, education, skills",
  "Use a clean resume format for better analysis",
];

export default function UploadPage() {
  const [fileName, setFileName] = useState("");
  const navigate = useNavigate();

  function handleFileChange(event) {
    const file = event.target.files?.[0];
    setFileName(file ? file.name : "");
  }

  function handleStartAnalysis() {
    if (!fileName) {
      return;
    }
    navigate("/processing");
  }

  return (
    <div className="site-page">
      <TopNav actions={[{ label: "Back to Home", to: "/", variant: "ghost" }]} compact />
      <main className="section-spacer">
        <div className="shell narrow-shell">
          <div className="page-intro center">
            <h1>Upload Your Resume</h1>
            <p>Upload your resume to get instant AI-powered analysis and feedback</p>
          </div>

          <section className="upload-card">
            <label className="dropzone">
              <input type="file" accept=".pdf,.docx" onChange={handleFileChange} />
              <span className="dropzone-icon">UP</span>
              <h2>Drag and drop your resume here</h2>
              <p>or click to browse files</p>
              <span className="nav-button primary small">Browse Files</span>
              <small>Supported formats: PDF, DOCX (Max 10MB)</small>
              {fileName ? <strong className="selected-file">Selected file: {fileName}</strong> : null}
            </label>

            <div className="upload-highlight-grid">
              {uploadHighlights.map((item) => (
                <article key={item.title} className="upload-highlight">
                  <span className="feature-icon blue">{item.icon}</span>
                  <div>
                    <strong>{item.title}</strong>
                    <small>{item.description}</small>
                  </div>
                </article>
              ))}
            </div>

            <div className="upload-actions">
              <button type="button" className="nav-button primary large" onClick={handleStartAnalysis}>
                Start Analysis
              </button>
              <Link className="nav-button secondary large" to="/job-descriptions">
                Manage Job Descriptions
              </Link>
            </div>
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
