import { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function RegisterPage() {
  const [form, setForm] = useState({
    full_name: "Nguyen Van A",
    email: "student@example.com",
    password: "password123",
  });
  const [message, setMessage] = useState("");

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Registration failed");
      }
      setMessage(`Created user: ${data.email}`);
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <section className="page split-page">
      <div className="panel accent-panel">
        <p className="eyebrow">User Setup</p>
        <h2>Create a test account</h2>
        <p>This gives the team a quick way to verify registration before wiring more protected flows in Week 7.</p>
      </div>
      <form className="panel form-panel" onSubmit={handleSubmit}>
        <h3>Register</h3>
        <label>
          Full name
          <input value={form.full_name} onChange={(event) => updateField("full_name", event.target.value)} />
        </label>
        <label>
          Email
          <input value={form.email} onChange={(event) => updateField("email", event.target.value)} type="email" />
        </label>
        <label>
          Password
          <input
            value={form.password}
            onChange={(event) => updateField("password", event.target.value)}
            type="password"
          />
        </label>
        <button type="submit">Create account</button>
        {message ? <p className="form-message">{message}</p> : null}
      </form>
    </section>
  );
}
