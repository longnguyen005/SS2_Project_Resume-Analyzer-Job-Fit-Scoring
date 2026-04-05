import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function OAuthCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login, refreshCurrentUser } = useAuth();

  useEffect(() => {
    async function completeOAuth() {
      const accessToken = searchParams.get("access_token");
      const provider = searchParams.get("provider");
      const error = searchParams.get("error");

      if (error) {
        navigate("/login", {
          replace: true,
          state: {
            flash: {
              type: "error",
              title: "Social Login Failed",
              message: error,
            },
          },
        });
        return;
      }

      if (!accessToken) {
        navigate("/login", {
          replace: true,
          state: {
            flash: {
              type: "error",
              title: "Social Login Failed",
              message: "No access token was returned from the OAuth provider.",
            },
          },
        });
        return;
      }

      login(accessToken);
      await refreshCurrentUser();

      navigate("/", {
        replace: true,
        state: {
          flash: {
            type: "success",
            title: "Signed In",
            message: `You are now signed in with ${provider || "your social account"}.`,
          },
        },
      });
    }

    completeOAuth();
  }, [login, navigate, refreshCurrentUser, searchParams]);

  return (
    <div className="processing-page">
      <div className="processing-shell">
        <section className="processing-card">
          <span className="processing-badge">AI</span>
          <h1>Signing You In</h1>
          <p>Completing your social login and returning you to the app...</p>
        </section>
      </div>
    </div>
  );
}
