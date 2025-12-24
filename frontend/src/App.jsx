import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import UploadResumes from "./pages/UploadResumes";
import ProtectedRoute from "./auth/ProtectedRoute";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ✅ DEFAULT ROUTE */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* ✅ Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* ✅ Protected route */}
        <Route
          path="/upload"
          element={
            <ProtectedRoute>
              <UploadResumes />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}