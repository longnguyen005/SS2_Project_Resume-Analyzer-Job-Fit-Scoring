import "./HistoryRow.css";

export default function HistoryRow({ item }) {
  return (
    <div className="history-row">
      <div className="history-file">
        <span className="feature-icon blue">CV</span>
        <div>
          <strong>{item.file}</strong>
          <small>{item.size}</small>
        </div>
      </div>
      <span>{item.date}</span>
      <div>
        <strong>{item.type}</strong>
        <small>File type</small>
      </div>
      <span>{item.size}</span>
      <span className={`status-pill ${item.status === "pending" ? "" : "completed"}`}>{item.status}</span>
      <div className="history-meta">
        <strong>{item.linkedJob}</strong>
        <small>Job description</small>
      </div>
    </div>
  );
}
