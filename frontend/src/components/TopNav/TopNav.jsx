import "./TopNav.css";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import BrandLogo from "../BrandLogo/BrandLogo";
import { useAuth } from "../../context/AuthContext";

export default function TopNav({ actions = [], compact = false }) {
  const location = useLocation();
  const navigate = useNavigate();
  const menuRef = useRef(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { currentUser, isAuthenticated, logout } = useAuth();

  const initial = useMemo(() => {
    const source = currentUser?.full_name?.trim() || currentUser?.email || "";
    return source ? source.charAt(0).toUpperCase() : "?";
  }, [currentUser]);

  useEffect(() => {
    setIsMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    function handlePointerDown(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
    };
  }, []);

  function handleLogout() {
    logout();
    setIsMenuOpen(false);
    navigate("/", { replace: true });
  }

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
          {isAuthenticated ? (
            <div className="user-menu" ref={menuRef}>
              <button
                type="button"
                className="avatar-button"
                onClick={() => setIsMenuOpen((current) => !current)}
                aria-haspopup="menu"
                aria-expanded={isMenuOpen}
                aria-label="Open account menu"
              >
                <span className="avatar-circle">{initial}</span>
              </button>

              {isMenuOpen ? (
                <div className="user-dropdown" role="menu">
                  <div className="user-dropdown-header">
                    <span className="avatar-circle large">{initial}</span>
                    <div>
                      <strong>{currentUser?.full_name || "Signed-in user"}</strong>
                      <small>{currentUser?.email || "Loading account..."}</small>
                    </div>
                  </div>
                  <Link className="user-dropdown-item" to="/profile" role="menuitem">
                    Profile / Settings
                  </Link>
                  <button type="button" className="user-dropdown-item danger" onClick={handleLogout} role="menuitem">
                    Log out
                  </button>
                </div>
              ) : null}
            </div>
          ) : null}
        </nav>
      </div>
    </header>
  );
}
