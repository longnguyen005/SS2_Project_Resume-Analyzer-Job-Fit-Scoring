import "./AuthFrame.css";
import { Link } from "react-router-dom";
import BrandLogo from "../BrandLogo/BrandLogo";
import { FaGoogle, FaGithub } from "react-icons/fa";
import { API_BASE_URL } from "../../lib/api";

export default function AuthFrame({
  title,
  subtitle,
  form,
  alternateText,
  alternateLink,
  alternateLabel,
  footerNote,
  extraPanel,
}) {
  return (
    <div className="auth-page">
      <div className="auth-shell">
        <Link className="back-link" to="/">
          &lt; Back to home
        </Link>
        <div className="auth-stack">
          <div className="auth-brand">
            <BrandLogo />
          </div>
          <section className="auth-card">
            <div className="auth-header">
              <h1>{title}</h1>
              <p>{subtitle}</p>
            </div>
            {form}
            <div className="auth-divider">
              <span>Or continue with</span>
            </div>
            <div className="auth-socials">
              <a href={`${API_BASE_URL}/auth/oauth/google/login`} className="social-button">
                <FaGoogle /> Google
              </a>
              <a href={`${API_BASE_URL}/auth/oauth/github/login`} className="social-button">
                <FaGithub /> GitHub
              </a>
            </div>
            <p className="auth-alternate">
              {alternateText} <Link to={alternateLink}>{alternateLabel}</Link>
            </p>
          </section>
          {extraPanel}
          <p className="auth-note">{footerNote}</p>
        </div>
      </div>
    </div>
  );
}
