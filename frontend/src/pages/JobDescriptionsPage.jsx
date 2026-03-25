import { jobDescriptions } from "../lib/mockData";

export default function JobDescriptionsPage() {
  return (
    <section className="page">
      <div className="panel panel-header-space">
        <div>
          <p className="eyebrow">Job Description Management</p>
          <h2>Static CRUD layout for Week 6</h2>
        </div>
        <button type="button">Add JD</button>
      </div>

      <div className="two-column">
        <form className="panel form-panel">
          <h3>Create job description</h3>
          <label>
            Title
            <input placeholder="Backend Engineer" />
          </label>
          <label>
            Description
            <textarea rows="8" placeholder="Paste the JD here..." />
          </label>
          <button type="button">Save JD</button>
        </form>

        <section className="panel">
          <div className="panel-header">
            <h3>Saved JDs</h3>
            <span className="badge">Mock list</span>
          </div>
          <div className="list">
            {jobDescriptions.map((item) => (
              <article key={item.id} className="list-card">
                <strong>{item.title}</strong>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
