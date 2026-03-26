import "./BrandLogo.css";
import { Link } from "react-router-dom";

export default function BrandLogo({ to = "/" }) {
  return (
    <Link className="brand-logo" to={to}>
      <span className="brand-mark">AI</span>
      <span className="brand-text">ResumeAI</span>
    </Link>
  );
}
