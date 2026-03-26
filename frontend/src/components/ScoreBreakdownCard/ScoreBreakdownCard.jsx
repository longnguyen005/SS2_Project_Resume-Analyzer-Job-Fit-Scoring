import "./ScoreBreakdownCard.css";

export default function ScoreBreakdownCard({ title, score, status, tone = "blue" }) {
  return (
    <article className="score-card">
      <h3>{title}</h3>
      <div className="score-value">
        <strong>{score}</strong>
        <span>/100</span>
      </div>
      <div className="score-bar">
        <span className={`score-fill ${tone}`} style={{ width: `${score}%` }} />
      </div>
      <small>{status}</small>
    </article>
  );
}
