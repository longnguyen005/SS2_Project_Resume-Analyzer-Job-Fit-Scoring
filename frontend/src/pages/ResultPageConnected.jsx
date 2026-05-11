import { useEffect, useMemo, useState } from "react";
import { Link, createSearchParams, useNavigate, useSearchParams } from "react-router-dom";
import LoadingSpinner from "../components/LoadingSpinner";
import ScoreBreakdownCard from "../components/ScoreBreakdownCard/ScoreBreakdownCard";
import SuggestionCard from "../components/SuggestionCard/SuggestionCard";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";
import { formatAnalysisProviderLabel, formatCvDateTime, normalizeResultData } from "../lib/cvReadModels";

export default function ResultPageConnected() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { logout } = useAuth();
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const cvId = searchParams.get("cvId");

  useEffect(() => {
    if (!cvId) {
      setIsLoading(false);
      setResult(null);
      setMessage("No CV result was selected. Please upload a resume first.");
      return;
    }

    loadResult();
  }, [cvId]);

  async function loadResult() {
    setIsLoading(true);
    setMessage("");

    try {
      const data = await apiRequest(`/cv/${cvId}/result`);
      setResult(normalizeResultData(data));
    } catch (error) {
      if (error.status === 401) {
        logout();
        navigate("/login", { replace: true });
        return;
      }

      if (error.status === 409) {
        setResult(null);
        setMessage(error.message || "The analysis is not completed yet. Please return to the processing page and wait a little longer.");
      } else {
        setResult(null);
        setMessage(error.message || "Unable to load CV result.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  const resultSearch = useMemo(() => {
    if (!cvId) {
      return "";
    }
    return createSearchParams({ cvId }).toString();
  }, [cvId]);

  const ringStyle = useMemo(() => {
    const score = result?.overall_score ?? 0;
    const degrees = Math.max(0, Math.min(score, 100)) * 3.6;
    return {
      background: `conic-gradient(var(--blue) 0 ${degrees}deg, #e4ebfb ${degrees}deg 360deg)`,
    };
  }, [result]);

  if (isLoading) {
    return <LoadingSpinner fullScreen label="Loading CV result..." />;
  }

  return (
    <div className="site-page">
      <TopNav
        actions={[
          { label: "View History", to: "/history", variant: "ghost" },
          { label: "Upload New CV", to: "/upload", variant: "primary" },
        ]}
        compact
      />
      <main className="section-spacer">
        <div className="shell report-shell">

          {message ? (
            <section className="report-section">
              <div className="empty-state">
                <strong>{message}</strong>
                <div className="hero-actions">
                  <button type="button" className="nav-button secondary" onClick={loadResult}>
                    Retry Loading Result
                  </button>
                  <Link className="nav-button primary" to="/upload">
                    Upload Another Resume
                  </Link>
                </div>
              </div>
            </section>
          ) : null}

          {!message && result ? (
            <>
              <div className="report-heading">
                <h1>Resume Analysis Report</h1>
                <p>
                  {result.filename} - {formatCvDateTime(result.analyzed_at)}
                </p>
                {result.analysis_provider ? <p>Analysis source: {formatAnalysisProviderLabel(result.analysis_provider)}</p> : null}
              </div>

              <section className="overview-panel">
                <div>
                  <p className="section-eyebrow">Overall Resume Score</p>
                  <div className="hero-score">
                    <strong>{result.overall_score}</strong>
                    <span>/100</span>
                  </div>
                  <span className="grade-pill">{result.grade}</span>
                  <p>{result.summary}</p>
                </div>
                <div className="ring-visual">
                  <div className="ring-circle" style={ringStyle}>
                    <div className="ring-inner" />
                  </div>
                </div>
              </section>

              <section className="report-section">
                <h2>Score Breakdown</h2>
                <div className="score-grid">
                  {result.breakdown.map((item) => (
                    <ScoreBreakdownCard key={item.title} {...item} />
                  ))}
                </div>
              </section>

              <section className="chart-grid">
                <article className="chart-card">
                  <h3>Skills Analysis</h3>
                  <p>Breakdown of your key competencies</p>
                  <div className="bar-chart">
                    {result.skill_chart.map((bar) => (
                      <div key={bar.label} className="bar-item">
                        <div className="bar-track">
                          <span style={{ height: `${bar.value}%` }} />
                        </div>
                        <small>{bar.label}</small>
                      </div>
                    ))}
                  </div>
                </article>

                <article className="chart-card">
                  <h3>Content Quality</h3>
                  <p>Distribution of resume content quality</p>
                  <div className="pie-visual">
                    <div className="pie-circle" />
                  </div>
                  <div className="legend-list">
                    {result.content_quality.map((item) => (
                      <div key={item.label} className="legend-item">
                        <span className={`legend-dot ${item.tone}`} />
                        <span>
                          {item.label}: {item.value}
                        </span>
                      </div>
                    ))}
                  </div>
                </article>
              </section>

              <section className="feedback-grid">
                <article className="feedback-card positive-card">
                  <h3>Strengths</h3>
                  <ul>
                    {result.strengths.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>

                <article className="feedback-card warning-card">
                  <h3>Areas for Improvement</h3>
                  <ul>
                    {result.improvements.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
              </section>

              <section className="report-section">
                <div className="section-heading">
                  <p className="section-eyebrow">AI-Powered Suggestions</p>
                  <h2>Actionable recommendations to improve your resume score</h2>
                </div>
                <div className="suggestion-list">
                  {result.suggestions.map((item) => (
                    <SuggestionCard key={item.title} {...item} />
                  ))}
                </div>
              </section>

              <section className="cta-banner compact-banner">
                <h2>Ready to optimize your resume?</h2>
                <p>Apply these suggestions and upload another version to compare your progress.</p>
                <div className="hero-actions center-actions">
                  <Link className="nav-button secondary large" to="/upload">
                    Upload New Version
                  </Link>
                  <Link className="nav-button outline large" to="/history">
                    View History
                  </Link>
                </div>
              </section>
            </>
          ) : null}

          {!message && !result ? (
            <section className="report-section">
              <div className="empty-state">
                <strong>No result data is available for this CV yet.</strong>
                <p>Please upload again or return from the processing flow.</p>
              </div>
            </section>
          ) : null}
        </div>
      </main>
    </div>
  );
}
