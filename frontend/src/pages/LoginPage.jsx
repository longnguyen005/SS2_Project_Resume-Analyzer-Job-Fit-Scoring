import { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function LoginPage() {
  const [email, setEmail] = useState("student@example.com");
  const [password, setPassword] = useState("password123");
  const [message, setMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const payload = new URLSearchParams();
    payload.append("username", email);
    payload.append("password", password);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: payload.toString(),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }
      localStorage.setItem("resume-analyzer-token", data.access_token);
      setMessage("Login success. Token saved to localStorage.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <section className="page split-page">
      <div className="panel accent-panel">
        <p className="eyebrow">Auth Flow</p>
        <h2>Sign in for Week 6 testing</h2>
        <p>Use this screen to verify the backend auth API and token storage flow before protected pages go live.</p>
      </div>
      <form className="panel form-panel" onSubmit={handleSubmit}>
        <h3>Login</h3>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
        </label>
        <label>
          Password
          <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" />
        </label>
        <button type="submit">Login</button>
        {message ? <p className="form-message">{message}</p> : null}
      </form>
    </section>
  );
}
