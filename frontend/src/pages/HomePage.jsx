import { Link, useLocation, useNavigate } from "react-router-dom";
import FeatureCard from "../components/FeatureCard/FeatureCard";
import Footer from "../components/Footer/Footer";
import SectionHeading from "../components/SectionHeading/SectionHeading";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { featureCards, homeTrustPills } from "../lib/mockData";


export default function HomePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();
  const flash = location.state?.flash;

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  const navActions = isAuthenticated
    ? [
        { label: "Dashboard", to: "/dashboard", variant: "ghost" },
        { label: "History", to: "/history", variant: "ghost" },
        { label: "Upload", to: "/upload", variant: "primary" },
      ]
    : [
        { label: "Login", to: "/login", variant: "ghost" },
        { label: "Sign Up", to: "/register", variant: "primary" },
      ];

  return (
    <div className="site-page">
      <TopNav actions={navActions} />
      <main>
        {flash ? (
          <section className="flash-shell">
            <div className={`shell flash-banner ${flash.type || "success"}`}>
              <strong>{flash.title}</strong>
              <p>{flash.message}</p>
            </div>
          </section>
        ) : null}
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
                <Link className="nav-button primary large" to={isAuthenticated ? "/upload" : "/login"}>
                  {isAuthenticated ? "Upload Resume" : "Login to Start"}
                </Link>
                <Link className="nav-button secondary large1" to={isAuthenticated ? "/job-descriptions" : "/result"}>
                  {isAuthenticated ? "Manage Job Descriptions" : "See Example Report"}
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
              <div className="preview-card-wrap">
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
              <h2>{isAuthenticated ? "Ready for the next action?" : "Ready to improve your resume?"}</h2>
              <p>
                {isAuthenticated
                  ? "Go to upload, review your history, or manage job descriptions from one place."
                  : "Create an account or sign in to start using the real backend flows."}
              </p>
              <Link className="nav-button secondary large" to={isAuthenticated ? "/upload" : "/login"}>
                {isAuthenticated ? "Go to Upload" : "Get Started"}
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
