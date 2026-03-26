import { Route, Routes } from "react-router-dom";
import HistoryPage from "./pages/HistoryPage";
import HomePage from "./pages/HomePage";
import JobDescriptionsPage from "./pages/JobDescriptionsPage";
import LoginPage from "./pages/LoginPage";
import ProcessingPage from "./pages/ProcessingPage";
import RegisterPage from "./pages/RegisterPage";
import ResultPage from "./pages/ResultPage";
import UploadPage from "./pages/UploadPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/job-descriptions" element={<JobDescriptionsPage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/processing" element={<ProcessingPage />} />
      <Route path="/history" element={<HistoryPage />} />
      <Route path="/result" element={<ResultPage />} />
    </Routes>
  );
}
