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
        <strong>{item.score}</strong>
        <small>{item.grade}</small>
      </div>
      <span className={`change-text ${item.change.startsWith("+") ? "positive" : "negative"}`}>{item.change}</span>
      <span className="status-pill completed">{item.status}</span>
      <div className="row-actions">
        <button type="button" className="table-button">
          View
        </button>
        <button type="button" className="table-icon">
          DL
        </button>
        <button type="button" className="table-icon danger">
          X
        </button>
      </div>
    </div>
  );
}
