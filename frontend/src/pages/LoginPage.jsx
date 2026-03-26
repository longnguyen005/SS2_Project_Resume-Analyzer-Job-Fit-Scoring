import { useState } from "react";
import AuthFrame from "../components/AuthFrame/AuthFrame";
import AuthInput from "../components/AuthInput/AuthInput";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function LoginPage() {
  const [email, setEmail] = useState("week6@example.com");
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
      setMessage("Login success. Access token saved for Week 6 protected flows.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  const form = (
    <form className="auth-form" onSubmit={handleSubmit}>
      <AuthInput
        label="Email"
        type="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        placeholder="name@example.com"
      />
      <AuthInput
        label="Password"
        type="password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        placeholder="Enter your password"
      />
      <button type="submit" className="nav-button primary full">
        Sign in
      </button>
      {message ? <p className="form-message success">{message}</p> : null}
    </form>
  );

  return (
    <AuthFrame
      title="Welcome back"
      subtitle="Sign in to your account to continue"
      form={form}
      alternateText="Don't have an account?"
      alternateLink="/register"
      alternateLabel="Sign up"
      footerNote="By continuing, you agree to our Terms of Service and Privacy Policy."
    />
  );
}
