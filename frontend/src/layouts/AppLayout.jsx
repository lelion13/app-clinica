import { Link, NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

const navLinkStyle = ({ isActive }) => ({
  padding: "8px 12px",
  borderRadius: 6,
  textDecoration: "none",
  color: isActive ? "#fff" : "#1e293b",
  backgroundColor: isActive ? "#0f766e" : "#f1f5f9",
  fontWeight: isActive ? 600 : 500,
  fontSize: "0.9rem",
  whiteSpace: "nowrap",
});

export function AppLayout() {
  const { user, isAdmin, logout } = useAuth();

  const doLogout = async () => {
    await logout();
    window.location.href = "/login";
  };

  return (
    <div style={{ minHeight: "100vh", background: "#fafafa" }}>
      <header
        style={{
          borderBottom: "1px solid #e2e8f0",
          background: "#fff",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div
          style={{
            maxWidth: 1100,
            margin: "0 auto",
            padding: "12px 16px",
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: "1.15rem", fontWeight: 700 }}>Clínica — Panel</div>
              <div style={{ fontSize: "0.85rem", color: "#64748b" }}>
                {user?.name} · {user?.role}
              </div>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <Link to="/setup" style={{ fontSize: "0.9rem", color: "#64748b" }}>
                Setup
              </Link>
              <button type="button" onClick={doLogout}>
                Cerrar sesión
              </button>
            </div>
          </div>

          <nav
            aria-label="Secciones"
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 8,
              alignItems: "center",
            }}
          >
            <NavLink to="/" end style={navLinkStyle}>
              Agenda
            </NavLink>
            <NavLink to="/ubicaciones" style={navLinkStyle}>
              Ubicaciones
            </NavLink>
            <NavLink to="/profesionales" style={navLinkStyle}>
              Profesionales
            </NavLink>
            <NavLink to="/consultorios" style={navLinkStyle}>
              Consultorios
            </NavLink>
            <NavLink to="/horarios-consultorio" style={navLinkStyle}>
              Horarios consultorio
            </NavLink>
            <NavLink to="/estadisticas" style={navLinkStyle}>
              Estadística
            </NavLink>
            {isAdmin ? (
              <NavLink to="/usuarios" style={navLinkStyle}>
                Usuarios
              </NavLink>
            ) : null}
          </nav>
        </div>
      </header>

      <main style={{ maxWidth: 1100, margin: "0 auto", padding: "20px 16px 40px" }}>
        <Outlet />
      </main>
    </div>
  );
}
