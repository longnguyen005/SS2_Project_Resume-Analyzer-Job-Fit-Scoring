import { summaryCards, uploadQueue } from "../lib/mockData";

export default function DashboardPage() {
  return (
    <section className="page">
      <div className="hero-card">
        <p className="eyebrow">Overview</p>
        <h2>Week 6 dashboard scaffold</h2>
        <p>
          This screen is ready for real API wiring in Week 7. For now it demonstrates the layout, navigation, and
          data shape the frontend will consume from the backend.
        </p>
      </div>

      <div className="card-grid">
        {summaryCards.map((card) => (
          <article key={card.label} className="metric-card">
            <span>{card.label}</span>
            <strong>{card.value}</strong>
            <small>{card.hint}</small>
          </article>
        ))}
      </div>

      <section className="panel">
        <div className="panel-header">
          <h3>Recent uploads</h3>
          <span className="badge">Mock data</span>
        </div>
        <div className="list">
          {uploadQueue.map((item) => (
            <div key={item.id} className="list-row">
              <div>
                <strong>{item.filename}</strong>
                <p>{item.createdAt}</p>
              </div>
              <span className={`status ${item.status}`}>{item.status}</span>
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}
