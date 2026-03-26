import "./FeatureCard.css";

export default function FeatureCard({ icon, title, description, accent }) {
  return (
    <article className="feature-card">
      <span className={`feature-icon ${accent}`}>{icon}</span>
      <h3>{title}</h3>
      <p>{description}</p>
    </article>
  );
}
