import { useState } from "react";
import AuthFrame from "../components/AuthFrame/AuthFrame";
import AuthInput from "../components/AuthInput/AuthInput";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
const benefitItems = ["Unlimited resume analyses", "Track your progress over time", "AI-powered suggestions"];

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

  const formView = (
    <form className="auth-form" onSubmit={handleSubmit}>
      <AuthInput
        label="Full Name"
        value={form.full_name}
        onChange={(event) => updateField("full_name", event.target.value)}
        placeholder="John Doe"
      />
      <AuthInput
        label="Email"
        type="email"
        value={form.email}
        onChange={(event) => updateField("email", event.target.value)}
        placeholder="name@example.com"
      />
      <AuthInput
        label="Password"
        type="password"
        value={form.password}
        onChange={(event) => updateField("password", event.target.value)}
        placeholder="Create a strong password"
        helper="Use at least 8 characters"
      />
      <label className="checkbox-row">
        <input type="checkbox" defaultChecked />
        <span>I agree to the Terms of Service and Privacy Policy</span>
      </label>
      <button type="submit" className="nav-button primary full">
        Create account
      </button>
      {message ? <p className="form-message success">{message}</p> : null}
    </form>
  );

  const extraPanel = (
    <div className="benefit-panel">
      {benefitItems.map((item) => (
        <div key={item} className="benefit-item">
          <span className="benefit-dot" />
          <span>{item}</span>
        </div>
      ))}
    </div>
  );

  return (
    <AuthFrame
      title="Create an account"
      subtitle="Start optimizing your resume with AI"
      form={formView}
      alternateText="Already have an account?"
      alternateLink="/login"
      alternateLabel="Sign in"
      footerNote="Week 6 keeps registration real, while the rest of the product remains static-first."
      extraPanel={extraPanel}
    />
  );
}
