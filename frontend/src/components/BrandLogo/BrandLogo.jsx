import "./BrandLogo.css";
import { Brain } from "lucide-react";
import { Link } from "react-router-dom";

export default function BrandLogo({ to = "/" }) {

  
  return (
    <Link className="brand-logo" to={to}>
      <Brain />
      <span className="brand-text">ResumeAI</span>
    </Link>
  );
}
