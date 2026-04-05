import { Component } from "react";
import { Link } from "react-router-dom";

export default class RouteErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMessage: "" };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      errorMessage: error instanceof Error ? error.message : "Unexpected route error.",
    };
  }

  componentDidCatch(error) {
    console.error("Route render error:", error);
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div className="site-page">
        <main className="section-spacer">
          <div className="shell report-shell">
            <section className="report-section">
              <div className="page-feedback error">
                <strong>We could not render this page.</strong>
                <p>{this.state.errorMessage || "Please refresh the page and try again."}</p>
              </div>
              <div className="hero-actions" style={{ marginTop: "1rem" }}>
                <button type="button" className="nav-button primary" onClick={() => window.location.reload()}>
                  Refresh Page
                </button>
                <Link className="nav-button outline" to="/">
                  Back To Home
                </Link>
              </div>
            </section>
          </div>
        </main>
      </div>
    );
  }
}
