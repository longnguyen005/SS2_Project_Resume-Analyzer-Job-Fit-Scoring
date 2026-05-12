import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";

export default function JobDescriptionsPage() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [form, setForm] = useState({
    title: "",
    description_text: "",
  });
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeItemId, setActiveItemId] = useState(null);
  const [deleteCandidate, setDeleteCandidate] = useState(null);

  useEffect(() => {
    loadJobDescriptions();
  }, []);

  async function loadJobDescriptions() {
    setIsLoading(true);
    setMessage("");

    try {
      const data = await apiRequest("/jd");
      setJobDescriptions(data);
    } catch (error) {
      handleProtectedPageError(error, "Cannot load the job description list.");
    } finally {
      setIsLoading(false);
    }
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSaving(true);
    setMessage("");

    try {
      const savedItem = editingId
        ? await apiRequest(`/jd/${editingId}`, {
            method: "PUT",
            body: JSON.stringify(form),
          })
        : await apiRequest("/jd", {
            method: "POST",
            body: JSON.stringify(form),
          });

      setJobDescriptions((current) =>
        editingId ? current.map((item) => (item.id === editingId ? savedItem : item)) : [savedItem, ...current],
      );
      setForm({ title: "", description_text: "" });
      setEditingId(null);
      setMessageType("success");
      setMessage(editingId ? "Job description updated." : "Job description saved.");
    } catch (error) {
      handleProtectedPageError(error, editingId ? "Unable to update job description." : "Unable to save job description.");
    } finally {
      setIsSaving(false);
    }
  }

  function handleEdit(item) {
    setEditingId(item.id);
    setForm({
      title: item.title,
      description_text: item.description_text,
    });
    setMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleCancelEdit() {
    setEditingId(null);
    setForm({ title: "", description_text: "" });
    setMessage("");
  }

  function handleRequestDelete(item) {
    setDeleteCandidate(item);
  }

  function handleCloseDeleteModal() {
    if (activeItemId) {
      return;
    }

    setDeleteCandidate(null);
  }

  async function handleConfirmDelete() {
    if (!deleteCandidate) {
      return;
    }

    const id = deleteCandidate.id;
    setActiveItemId(id);
    setMessage("");

    try {
      await apiRequest(`/jd/${id}`, {
        method: "DELETE",
      });

      setJobDescriptions((current) => current.filter((item) => item.id !== id));
      if (editingId === id) {
        handleCancelEdit();
      }
      setMessageType("success");
      setMessage("Job description deleted.");
      setDeleteCandidate(null);
    } catch (error) {
      handleProtectedPageError(error, "Unable to delete job description.");
    } finally {
      setActiveItemId(null);
    }
  }

  function handleProtectedPageError(error, fallbackMessage) {
    if (error.status === 401) {
      logout();
      navigate("/login", { replace: true });
      return;
    }

    setMessageType("error");
    setMessage(error.message || fallbackMessage);
  }

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
              <h2>{editingId ? "Update Job Description" : "Create Job Description"}</h2>
              <form className="jd-form-stack" onSubmit={handleSubmit}>
                <label className="auth-field">
                  <span>Title</span>
                  <input
                    value={form.title}
                    onChange={(event) => updateField("title", event.target.value)}
                    placeholder="eg. Backend Engineer"
                  />
                </label>
                <label className="auth-field">
                  <span>Description</span>
                  <textarea
                    rows="8"
                    value={form.description_text}
                    onChange={(event) => updateField("description_text", event.target.value)}
                    placeholder="Paste the job description here..."
                  />
                </label>
                <div className="jd-form-actions">
                  <button type="submit" className="nav-button primary full" disabled={isSaving}>
                    {isSaving ? (editingId ? "Updating..." : "Saving...") : editingId ? "Update Job Description" : "Save Job Description"}
                  </button>
                  {editingId ? (
                    <button type="button" className="nav-button secondary full" onClick={handleCancelEdit} disabled={isSaving}>
                      Cancel
                    </button>
                  ) : null}
                </div>
                {message ? <p className={`page-feedback ${messageType}`}>{message}</p> : null}
              </form>
            </section>

            <section className="jd-list-card">
              <h2>Saved Job Descriptions</h2>
              <div className="jd-list">
                {isLoading ? <p className="page-feedback">Loading data ...</p> : null}
                {!isLoading && messageType === "error" && message ? (
                  <div className="empty-state">
                    <strong>{message}</strong>
                    <button type="button" className="nav-button secondary" onClick={loadJobDescriptions}>
                      Retry
                    </button>
                  </div>
                ) : null}
                {!isLoading && !message && jobDescriptions.length === 0 ? (
                  <div className="empty-state">
                    <strong>There is no job description yet.</strong>
                    <p>Let's create the first Job Description</p>
                  </div>
                ) : null}
                {!message || messageType !== "error" ? jobDescriptions.map((item) => (
                  <article key={item.id} className="jd-item">
                    <div className="panel-header">
                      <strong>{item.title}</strong>
                      <span className="status-pill completed">Saved</span>
                    </div>
                    <p>{item.description_text}</p>
                    <div className="jd-item-actions">
                      <button
                        type="button"
                        className="nav-button secondary small"
                        onClick={() => handleEdit(item)}
                        disabled={isSaving || activeItemId === item.id}
                      >
                        {editingId === item.id ? "Editing" : "Edit"}
                      </button>
                      <button
                        type="button"
                        className="nav-button ghost small jd-delete-button"
                        onClick={() => handleRequestDelete(item)}
                        disabled={activeItemId === item.id}
                      >
                        {activeItemId === item.id ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </article>
                )) : null}
              </div>
            </section>
          </div>
        </div>
      </main>
      {deleteCandidate ? (
        <div className="confirm-overlay" role="presentation" onClick={handleCloseDeleteModal}>
          <div
            className="confirm-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-jd-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="confirm-dialog-content">
              <h2 id="delete-jd-title">Delete this job description?</h2>
              <p>
                <strong>{deleteCandidate.title}</strong> will be removed from your library. This action cannot be undone.
              </p>
            </div>
            <div className="confirm-dialog-actions">
              <button
                type="button"
                className="nav-button secondary"
                onClick={handleCloseDeleteModal}
                disabled={Boolean(activeItemId)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="nav-button primary jd-confirm-delete"
                onClick={handleConfirmDelete}
                disabled={Boolean(activeItemId)}
              >
                {activeItemId ? "Deleting..." : "Yes"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
