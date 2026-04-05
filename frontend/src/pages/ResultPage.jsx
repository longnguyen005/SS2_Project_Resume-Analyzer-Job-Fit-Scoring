import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import LoadingSpinner from "../components/LoadingSpinner";
import ScoreBreakdownCard from "../components/ScoreBreakdownCard/ScoreBreakdownCard";
import SuggestionCard from "../components/SuggestionCard/SuggestionCard";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";

export default function ResultPage() {
  return (
    <div className="site-page">
      <TopNav
        actions={[
          { label: "View History", to: "/history", variant: "ghost" },
          { label: "Export Report", to: "/result", variant: "secondary" },
          { label: "Share", to: "/result", variant: "primary" },
        ]}
        compact
      />
      <main className="section-spacer">
        <div className="shell report-shell">
          <Link className="back-link" to="/upload">
            ← Analyze Another Resume
          </Link>
          <div className="report-heading">
            <h1>Resume Analysis Report</h1>
            <p>John_Doe_Resume.pdf · March 16, 2026</p>
          </div>

          <section className="overview-panel">
            <div>
              <p className="section-eyebrow">Overall Resume Score</p>
              <div className="hero-score">
                <strong>87</strong>
                <span>/100</span>
              </div>
              <span className="grade-pill">Very Good</span>
              <p>Your resume is performing well. Check the suggestions below to make it even better.</p>
            </div>
            <div className="ring-visual">
              <div className="ring-circle">
                <div className="ring-inner" />
              </div>
            </div>
          </section>

          <section className="report-section">
            <h2>Score Breakdown</h2>
            <div className="score-grid">
              {resultBreakdown.map((item) => (
                <ScoreBreakdownCard key={item.title} {...item} />
              ))}
            </div>
          </section>

          <section className="chart-grid">
            <article className="chart-card">
              <h3>Skills Analysis</h3>
              <p>Breakdown of your key competencies</p>
              <div className="bar-chart">
                {skillChartBars.map((bar) => (
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
                {contentQualityLegend.map((item) => (
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
                {resultStrengths.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>

            <article className="feedback-card warning-card">
              <h3>Areas for Improvement</h3>
              <ul>
                {areasForImprovement.map((item) => (
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
              {resultSuggestions.map((item) => (
                <SuggestionCard key={item.title} {...item} />
              ))}
            </div>
          </section>

          <section className="cta-banner compact-banner">
            <h2>Ready to optimize your resume?</h2>
            <p>Apply these suggestions and re-upload to see your score improve</p>
            <div className="hero-actions center-actions">
              <Link className="nav-button secondary large" to="/upload">
                Upload New Version
              </Link>
              <Link className="nav-button outline large" to="/result">
                Download Suggestions
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
