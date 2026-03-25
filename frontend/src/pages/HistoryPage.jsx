import { uploadQueue } from "../lib/mockData";

export default function HistoryPage() {
  return (
    <section className="page">
      <div className="panel">
        <p className="eyebrow">Analysis History</p>
        <h2>Week 6 preview of user history</h2>
        <p>This table shows the shape expected from `GET /api/v1/cv` once the frontend is wired to real data.</p>
      </div>

      <section className="panel">
        <div className="table-grid table-header">
          <span>Filename</span>
          <span>Status</span>
          <span>Created</span>
        </div>
        {uploadQueue.map((item) => (
          <div key={item.id} className="table-grid">
            <strong>{item.filename}</strong>
            <span className={`status ${item.status}`}>{item.status}</span>
            <span>{item.createdAt}</span>
          </div>
        ))}
      </section>
    </section>
  );
}
