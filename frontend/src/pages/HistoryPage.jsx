import HistoryRow from "../components/HistoryRow/HistoryRow";
import MetricTile from "../components/MetricTile/MetricTile";
import TopNav from "../components/TopNav/TopNav";
import { historyItems, historyMetrics, progressJourney } from "../lib/mockData";

export default function HistoryPage() {
  return (
    <div className="site-page">
      <TopNav actions={[{ label: "Upload New Resume", to: "/upload", variant: "primary" }]} compact />
      <main className="section-spacer">
        <div className="shell report-shell">
          <div className="page-intro">
            <h1>Resume History</h1>
            <p>Track your resume improvements and view past analyses</p>
          </div>

          <div className="metric-grid">
            {historyMetrics.map((item) => (
              <MetricTile key={item.label} {...item} />
            ))}
          </div>

          <section className="journey-card">
            <h2>Your Progress Journey</h2>
            <p>You've improved your resume score by 19 points since you started!</p>
            <div className="journey-points">
              {progressJourney.map((item) => (
                <div key={item.version} className="journey-point">
                  <strong>{item.score}</strong>
                  <small>{item.version}</small>
                </div>
              ))}
            </div>
          </section>

          <section className="history-card">
            <div className="section-heading">
              <h2>Analysis History</h2>
              <p>View and manage your past resume analyses</p>
            </div>
            <div className="history-table">
              <div className="history-header">
                <span>Resume File</span>
                <span>Upload Date</span>
                <span>Score</span>
                <span>Change</span>
                <span>Status</span>
                <span>Actions</span>
              </div>
              {historyItems.map((item) => (
                <HistoryRow key={item.file} item={item} />
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
