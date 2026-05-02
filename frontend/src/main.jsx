import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider } from "./auth/AuthContext";
import { AppLayout } from "./layouts/AppLayout";
import { AgendaPage } from "./pages/AgendaPage";
import { ConsultingRoomsPage } from "./pages/ConsultingRoomsPage";
import { LocationsPage } from "./pages/LocationsPage";
import { LoginPage } from "./pages/LoginPage";
import { ProfessionalsPage } from "./pages/ProfessionalsPage";
import { RoomHoursPage } from "./pages/RoomHoursPage";
import { SetupPage } from "./pages/SetupPage";
import { UsersPage } from "./pages/UsersPage";
import { ProtectedRoute } from "./router/ProtectedRoute";

function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/setup" element={<SetupPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AgendaPage />} />
        <Route path="ubicaciones" element={<LocationsPage />} />
        <Route path="profesionales" element={<ProfessionalsPage />} />
        <Route path="consultorios" element={<ConsultingRoomsPage />} />
        <Route path="horarios-consultorio" element={<RoomHoursPage />} />
        <Route
          path="usuarios"
          element={
            <ProtectedRoute adminOnly>
              <UsersPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
