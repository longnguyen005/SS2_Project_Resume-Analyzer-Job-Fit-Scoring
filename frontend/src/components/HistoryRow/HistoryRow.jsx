import { Link } from "react-router-dom";
import "./HistoryRow.css";

export default function HistoryRow({ item }) {
  const statusClassName = `status-pill${
    item.status === "completed" ? " completed" : item.status === "failed" ? " failed" : ""
  }`;

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
        <small>Overall score</small>
      </div>
      <div>
        <strong>{item.grade}</strong>
        <small>Analysis grade</small>
      </div>
      <span className={statusClassName}>{item.status}</span>
      <div className="history-meta">
        {item.canViewResult ? (
          <Link className="table-button" to={`/result?cvId=${item.id}`}>
            View Result
          </Link>
        ) : (
          <>
            <strong>Unavailable</strong>
            <small>Result not ready yet</small>
          </>
        )}
      </div>
    </div>
  );
}
