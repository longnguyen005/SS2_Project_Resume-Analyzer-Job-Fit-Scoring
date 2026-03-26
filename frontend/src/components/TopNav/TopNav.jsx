import "./TopNav.css";
import { Link } from "react-router-dom";
import BrandLogo from "../BrandLogo/BrandLogo";

export default function TopNav({ actions = [], compact = false }) {
  return (
    <header className={`top-nav${compact ? " compact" : ""}`}>
      <div className="shell top-nav-inner">
        <BrandLogo />
        <nav className="top-nav-actions">
          {actions.map((action) =>
            action.to ? (
              <Link
                key={`${action.label}-${action.to}`}
                to={action.to}
                className={`nav-button${action.variant ? ` ${action.variant}` : ""}`}
              >
                {action.label}
              </Link>
            ) : (
              <button
                key={action.label}
                type={action.type || "button"}
                className={`nav-button${action.variant ? ` ${action.variant}` : ""}`}
                onClick={action.onClick}
              >
                {action.label}
              </button>
            ),
          )}
        </nav>
      </div>
    </header>
  );
}
