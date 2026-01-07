import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import UploadResumes from "./pages/UploadResumes";
import HistoryPage from "./pages/HistoryPage";
import ProtectedRoute from "./auth/ProtectedRoute";
import HistoryDetail from "./pages/HistoryDetail";
import Landing from "./pages/Landing";
import { useAuth } from "./auth/AuthContext";

function PublicRoute({ children }) {
  const { token } = useAuth();
  return token ? <Navigate to="/upload" replace /> : children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route
          path="/"
          element={
              <Landing />
          }
        />

        <Route
          path="/login"
          element={
              <Login />
          }
        />

        <Route
          path="/register"
          element={
              <Register />
          }
        />

        {/* Protected */}
        <Route
          path="/upload"
          element={
            <ProtectedRoute>
              <UploadResumes />
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

        <Route
          path="/history/:sessionId"
          element={
            <ProtectedRoute>
              <HistoryDetail />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}