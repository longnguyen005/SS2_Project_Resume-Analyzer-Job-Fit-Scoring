import { Link } from "react-router-dom";
import FeatureCard from "../components/FeatureCard/FeatureCard";
import Footer from "../components/Footer/Footer";
import SectionHeading from "../components/SectionHeading/SectionHeading";
import TopNav from "../components/TopNav/TopNav";
import { featureCards, homeTrustPills } from "../lib/mockData";

export default function HomePage() {
  return (
    <div className="site-page">
      <TopNav
        actions={[
          { label: "Login", to: "/login", variant: "ghost" },
          { label: "Sign Up", to: "/register", variant: "primary" },
        ]}
      />
      <main>
        <section className="hero-section">
          <div className="shell hero-grid">
            <div className="hero-copy">
              <span className="section-badge">AI-Powered Resume Analysis</span>
              <h1>Analyze Your Resume with AI</h1>
              <p>
                Get instant, AI-powered feedback on your resume. Discover your strengths, identify areas for
                improvement, and optimize your job application success rate.
              </p>
              <div className="hero-actions">
                <Link className="nav-button primary large" to="/upload">
                  Upload Resume
                </Link>
                <Link className="nav-button secondary large" to="/result">
                  See Example Report
                </Link>
              </div>
              <div className="trust-row">
                {homeTrustPills.map((item) => (
                  <span key={item} className="trust-pill">
                    {item}
                  </span>
                ))}
              </div>
            </div>
            <div className="hero-preview">
              <div className="preview-card">
                <div className="preview-lines">
                  <span className="preview-icon">CV</span>
                  <div className="preview-block">
                    <span className="line short" />
                    <span className="line medium" />
                    <span className="line full" />
                    <span className="line medium" />
                  </div>
                </div>
                <div className="score-preview">
                  <div>
                    <small>Resume Score</small>
                    <strong>87/100</strong>
                  </div>
                  <span className="feature-icon purple">AI</span>
                  <div className="gradient-bar">
                    <span />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="section-spacer">
          <div className="shell">
            <SectionHeading center title="Powerful Features" description="Everything you need to perfect your resume" />
            <div className="feature-grid">
              {featureCards.map((feature) => (
                <FeatureCard key={feature.title} {...feature} />
              ))}
            </div>
          </div>
        </section>
        <section className="section-spacer">
          <div className="shell">
            <div className="cta-banner">
              <h2>Ready to improve your resume?</h2>
              <p>Upload your resume now and get instant AI-powered feedback</p>
              <Link className="nav-button secondary large" to="/upload">
                Get Started for Free
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
