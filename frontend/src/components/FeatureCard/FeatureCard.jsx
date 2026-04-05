import "./FeatureCard.css";

export default function FeatureCard({ icon, title, description, accent }) {
  const Icon = icon;

  return (
    <article className="feature-card">
      <span className={`feature-icon ${accent}`}>{Icon ? <Icon size={18} strokeWidth={2.2} /> : null}</span>
      <h3>{title}</h3>
      <p>{description}</p>
    </article>
  );
}
