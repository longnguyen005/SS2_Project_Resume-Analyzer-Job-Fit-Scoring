import "./SuggestionCard.css";

export default function SuggestionCard({ title, description, priority, tone }) {
  return (
    <article className={`suggestion-card ${tone}`}>
      <div className="suggestion-header">
        <h3>{title}</h3>
        <span className="priority-pill">{priority}</span>
      </div>
      <p>{description}</p>
      <button type="button" className="secondary-button small">
        Learn More
      </button>
    </article>
  );
}
