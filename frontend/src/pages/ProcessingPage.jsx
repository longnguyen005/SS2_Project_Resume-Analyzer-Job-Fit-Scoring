import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import BrandLogo from "../components/BrandLogo/BrandLogo";
import ProgressStep from "../components/ProgressStep/ProgressStep";
import { processingSteps } from "../lib/mockData";

export default function ProcessingPage() {
  const navigate = useNavigate();
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const stepDurations = [1800, 1800, 1600];
    const timers = [];

    stepDurations.forEach((duration, index) => {
      const totalDelay = stepDurations.slice(0, index + 1).reduce((sum, value) => sum + value, 0);
      timers.push(
        window.setTimeout(() => {
          if (index < stepDurations.length - 1) {
            setActiveIndex(index + 1);
          } else {
            navigate("/result");
          }
        }, totalDelay),
      );
    });

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, [navigate]);

  const progress = useMemo(() => {
    const checkpoints = [25, 68, 100];
    return checkpoints[Math.min(activeIndex, checkpoints.length - 1)];
  }, [activeIndex]);

  const stepViews = useMemo(
    () =>
      processingSteps.map((step, index) => {
        if (index < activeIndex) {
          return { ...step, state: "completed", badge: "Completed" };
        }
        if (index === activeIndex) {
          return { ...step, state: "active", badge: "Processing" };
        }
        return { ...step, state: "pending", badge: "Waiting" };
      }),
    [activeIndex],
  );

  return (
    <div className="processing-page">
      <div className="processing-shell">
        <BrandLogo />
        <section className="processing-card">
          <span className="processing-badge">AI</span>
          <h1>Analyzing Your Resume</h1>
          <p>Our AI is working its magic...</p>
          <div className="overall-progress">
            <div className="panel-header">
              <strong>Overall Progress</strong>
              <span>{progress}%</span>
            </div>
            <div className="score-bar">
              <span className="score-fill blue" style={{ width: `${progress}%` }} />
            </div>
          </div>
          <div className="progress-list">
            {stepViews.map((step) => (
              <ProgressStep key={step.title} {...step} />
            ))}
          </div>
          <div className="processing-note">This usually takes 10-15 seconds. Please don't close this window.</div>
        </section>
        <p className="tiny-note">
          <span className="spark">!</span> Did you know? Recruiters spend an average of 6 seconds reviewing a resume.
        </p>
        <Link className="back-link center-link" to="/result">
          Skip to mock result
        </Link>
      </div>
    </div>
  );
}
