import { Suspense, lazy } from "react";
import { Route, Routes } from "react-router-dom";
import LoadingSpinner from "./components/LoadingSpinner";
import ProtectedRoute from "./components/ProtectedRoute";
import RouteErrorBoundary from "./components/RouteErrorBoundary";

const HistoryPage = lazy(() => import("./pages/HistoryPage"));
const HomePage = lazy(() => import("./pages/HomePage"));
const JobDescriptionsPage = lazy(() => import("./pages/JobDescriptionsPage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const OAuthCallbackPage = lazy(() => import("./pages/OAuthCallbackPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const ProcessingPage = lazy(() => import("./pages/ProcessingPage"));
const RegisterPage = lazy(() => import("./pages/RegisterPage"));
const ResultPage = lazy(() => import("./pages/ResultPageConnected"));
const UploadPage = lazy(() => import("./pages/UploadPage"));

export default function App() {
  return (
    <RouteErrorBoundary>
      <Suspense fallback={<LoadingSpinner fullScreen label="Loading page..." />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
          <Route
            path="/job-descriptions"
            element={
              <ProtectedRoute>
                <JobDescriptionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ProtectedRoute>
                <UploadPage />
              </ProtectedRoute>
            }
          />
          <Route path="/processing" element={<ProcessingPage />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <HistoryPage />
              </ProtectedRoute>
            }
          />
          <Route path="/result" element={<ResultPage />} />
        </Routes>
      </Suspense>
    </RouteErrorBoundary>
  );
}
