import "./MetricTile.css";

export default function MetricTile({ icon, label, value, note, accent }) {
  return (
    <article className="metric-tile">
      <span className={`feature-icon ${accent}`}>{icon}</span>
      <small>{label}</small>
      <strong>{value}</strong>
      {note ? <p>{note}</p> : null}
    </article>
  );
}
