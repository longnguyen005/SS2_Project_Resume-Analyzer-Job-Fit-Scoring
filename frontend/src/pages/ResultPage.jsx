import { resultBreakdown, suggestions } from "../lib/mockData";

export default function ResultPage() {
  return (
    <section className="page">
      <div className="hero-card">
        <p className="eyebrow">Analysis Result</p>
        <h2>Sample result detail page</h2>
        <p>This is a static contract-first layout for the detailed score view that will be connected after AI flow.</p>
      </div>

      <div className="card-grid">
        <article className="metric-card">
          <span>Overall Score</span>
          <strong>78</strong>
          <small>Target role: Backend Engineer</small>
        </article>
        <article className="metric-card">
          <span>Language</span>
          <strong>EN</strong>
          <small>Detected from upload</small>
        </article>
      </div>

      <div className="two-column">
        <section className="panel">
          <h3>Score breakdown</h3>
          <div className="list">
            {resultBreakdown.map((item) => (
              <div key={item.category} className="list-card">
                <div className="panel-header">
                  <strong>{item.category}</strong>
                  <span className="badge">{item.score}/100</span>
                </div>
                <p>{item.feedback}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <h3>Suggestions</h3>
          <div className="list">
            {suggestions.map((item) => (
              <div key={item} className="list-card">
                <p>{item}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
