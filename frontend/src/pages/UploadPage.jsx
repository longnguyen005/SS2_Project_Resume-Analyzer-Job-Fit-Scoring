export default function UploadPage() {
  return (
    <section className="page">
      <div className="panel panel-header-space">
        <div>
          <p className="eyebrow">CV Upload</p>
          <h2>Upload flow scaffold</h2>
          <p>Week 6 stops at file submission and metadata creation. AI scoring will be added in later weeks.</p>
        </div>
        <span className="badge">Ready for multipart API</span>
      </div>

      <form className="panel form-panel">
        <label>
          Resume file
          <input type="file" accept=".pdf,.docx" />
        </label>
        <label>
          Optional job description
          <select defaultValue="">
            <option value="">No JD selected</option>
            <option value="jd-1">Backend Engineer</option>
            <option value="jd-2">AI Engineer</option>
          </select>
        </label>
        <button type="button">Upload and create record</button>
      </form>
    </section>
  );
}
