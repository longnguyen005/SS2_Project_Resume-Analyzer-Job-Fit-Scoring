import { NavLink, Route, Routes } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import HistoryPage from "./pages/HistoryPage";
import JobDescriptionsPage from "./pages/JobDescriptionsPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ResultPage from "./pages/ResultPage";
import UploadPage from "./pages/UploadPage";

const navigation = [
  { to: "/", label: "Dashboard" },
  { to: "/login", label: "Login" },
  { to: "/register", label: "Register" },
  { to: "/job-descriptions", label: "Job Descriptions" },
  { to: "/upload", label: "Upload CV" },
  { to: "/history", label: "History" },
  { to: "/result", label: "Result" },
];

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Week 6 Build</p>
          <h1>Resume Analyzer</h1>
          <p className="sidebar-copy">
            Static-first UI scaffold for auth, JD management, upload, history, and result views.
          </p>
        </div>
        <nav className="nav-list">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="page-content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/job-descriptions" element={<JobDescriptionsPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/result" element={<ResultPage />} />
        </Routes>
      </main>
    </div>
  );
}
