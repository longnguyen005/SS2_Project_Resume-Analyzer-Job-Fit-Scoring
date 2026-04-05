import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthFrame from "../components/AuthFrame/AuthFrame";
import AuthInput from "../components/AuthInput/AuthInput";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";

const benefitItems = ["Unlimited resume analyses", "Track your progress over time", "AI-powered suggestions"];

export default function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setMessage("");

    try {
      const data = await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setMessageType("success");
      setMessage(`Account created successfully for ${data.email}. Redirecting to sign in...`);
      window.setTimeout(() => {
        navigate("/login", {
          replace: true,
          state: {
            flash: {
              type: "success",
              title: "Account Created",
              message: `Your account for ${data.email} is ready. Please sign in to continue.`,
            },
          },
        });
      }, 900);
    } catch (error) {
      setMessageType("error");
      setMessage(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  const formView = (
    <form className="auth-form" onSubmit={handleSubmit}>
      <AuthInput
        label="Full Name"
        value={form.full_name}
        onChange={(event) => updateField("full_name", event.target.value)}
        placeholder="Enter your name"
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
        {isSubmitting ? "Creating account..." : "Create account"}
      </button>
      {message ? <p className={`form-message ${messageType}`}>{message}</p> : null}
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
      extraPanel={extraPanel}
    />
  );
}
