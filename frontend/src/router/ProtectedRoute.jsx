import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export function ProtectedRoute({ children, adminOnly = false, roles = null }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <p>Cargando sesion...</p>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && user.role !== "admin") {
    return <Navigate to="/" replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}
