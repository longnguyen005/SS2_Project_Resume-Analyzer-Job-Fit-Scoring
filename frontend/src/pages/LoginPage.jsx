import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AuthFrame from "../components/AuthFrame/AuthFrame";
import AuthInput from "../components/AuthInput/AuthInput";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";

export default function LoginPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const flash = location.state?.flash;
    if (!flash) {
      return;
    }

    setMessageType(flash.type || "success");
    setMessage(flash.message);
  }, [location.state]);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setMessage("");

    const payload = new URLSearchParams();
    payload.append("username", email);
    payload.append("password", password);

    try {
      const data = await apiRequest("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: payload.toString(),
      });
      login(data.access_token);
      setMessageType("success");
      setMessage("Signed in successfully. Redirecting to the home page...");
    } catch (error) {
      setMessageType("error");
      setMessage(error.message);
    } finally {
      setIsSubmitting(false);
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
      <button type="submit" className="nav-button primary full" disabled={isSubmitting}>
        {isSubmitting ? (
          <>
            <LoadingSpinner inline size={16} label="" />
            Signing in...
          </>
        ) : (
          "Sign in"
        )}
      </button>
      {message ? <p className={`form-message ${messageType}`}>{message}</p> : null}
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
