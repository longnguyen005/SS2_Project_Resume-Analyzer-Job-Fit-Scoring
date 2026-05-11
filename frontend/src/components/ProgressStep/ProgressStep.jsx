import "./ProgressStep.css";

export default function ProgressStep({ icon, title, description, state, badge }) {
  const displayIcon = state === "completed" ? "OK" : state === "failed" ? "!" : icon;
  return (
    <article className={`progress-step ${state}`}>
      <span className={`progress-icon ${state}`}>{displayIcon}</span>
      <div>
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      {badge ? <span className={`mini-badge ${state}`}>{badge}</span> : null}
    </article>
  );
}
