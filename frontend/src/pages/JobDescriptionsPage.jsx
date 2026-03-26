import TopNav from "../components/TopNav/TopNav";
import { jobDescriptions } from "../lib/mockData";

export default function JobDescriptionsPage() {
  return (
    <div className="site-page">
      <TopNav
        actions={[
          { label: "Back to Home", to: "/", variant: "ghost" },
          { label: "Upload Resume", to: "/upload", variant: "primary" },
        ]}
        compact
      />
      <main className="section-spacer">
        <div className="shell report-shell">
          <div className="page-intro">
            <h1>Job Description Library</h1>
          </div>

          <div className="jd-layout">
            <section className="jd-form-card">
              <h2>Create Job Description</h2>
              <label className="auth-field">
                <span>Title</span>
                <input placeholder="Backend Engineer" />
              </label>
              <label className="auth-field">
                <span>Description</span>
                <textarea rows="8" placeholder="Paste the job description here..." />
              </label>
              <button type="button" className="nav-button primary full">
                Save Job Description
              </button>
            </section>

            <section className="jd-list-card">
              <h2>Saved Job Descriptions</h2>
              <div className="jd-list">
                {jobDescriptions.map((item) => (
                  <article key={item.id} className="jd-item">
                    <div className="panel-header">
                      <strong>{item.title}</strong>
                      <span className="status-pill completed">Saved</span>
                    </div>
                    <p>{item.description}</p>
                  </article>
                ))}
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
