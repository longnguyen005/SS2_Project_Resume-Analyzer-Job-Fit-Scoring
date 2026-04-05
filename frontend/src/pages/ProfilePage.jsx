import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopNav from "../components/TopNav/TopNav";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../lib/api";

export default function ProfilePage() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    setIsLoading(true);
    setMessage("");

    try {
      const data = await apiRequest("/auth/me");
      setProfile(data);
    } catch (error) {
      if (error.status === 401) {
        logout();
        navigate("/login", { replace: true });
        return;
      }

      setMessage(error.message || "Could not load your profile.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  return (
    <div className="site-page">
      <TopNav
        actions={[
          { label: "Back to Home", to: "/", variant: "ghost" },
          { label: "History", to: "/history", variant: "secondary" },
        ]}
        compact
      />
      <main className="section-spacer">
        <div className="shell narrow-shell">
          <div className="page-intro center">
            <h1>Your Profile</h1>
          </div>

          <section className="profile-card">
            {isLoading ? <p className="page-feedback">Loading your profile...</p> : null}
            {!isLoading && message ? <p className="page-feedback error">{message}</p> : null}
            {!isLoading && profile ? (
              <div className="profile-grid">
                <div className="profile-item">
                  <small>Full Name</small>
                  <strong>{profile.full_name}</strong>
                </div>
                <div className="profile-item">
                  <small>Email</small>
                  <strong>{profile.email}</strong>
                </div>
                <div className="profile-item">
                  <small>User ID</small>
                  <strong>{profile.id}</strong>
                </div>
                <div className="profile-item">
                  <small>Status</small>
                  <strong>{profile.is_active ? "Active" : "Inactive"}</strong>
                </div>
                <div className="profile-item">
                  <small>Created At</small>
                  <strong>{new Date(profile.created_at).toLocaleString("vi-VN")}</strong>
                </div>
              </div>
            ) : null}
          </section>
        </div>
      </main>
    </div>
  );
}
