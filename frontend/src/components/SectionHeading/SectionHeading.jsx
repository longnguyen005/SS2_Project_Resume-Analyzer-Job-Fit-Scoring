import "./SectionHeading.css";

export default function SectionHeading({ eyebrow, title, description, center = false }) {
  return (
    <div className={`section-heading${center ? " center" : ""}`}>
      {eyebrow ? <p className="section-eyebrow">{eyebrow}</p> : null}
      <h2>{title}</h2>
      {description ? <p>{description}</p> : null}
    </div>
  );
}
