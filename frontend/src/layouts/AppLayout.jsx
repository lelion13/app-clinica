import { Link, NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { DistributionNavMenu } from "../components/DistributionNavMenu";
import { USERS_NAV_ITEM } from "../config/navigation";
import { navPillStyle, uiStyles, uiTheme } from "../ui/theme";

const navLinkStyle = ({ isActive }) => ({
  ...navPillStyle(isActive),
});

export function AppLayout() {
  const { user, isAdmin, logout } = useAuth();

  const doLogout = async () => {
    await logout();
    window.location.href = "/login";
  };

  return (
    <div style={{ minHeight: "100vh", background: uiTheme.colors.pageBg }}>
      <header
        style={{
          borderBottom: `1px solid ${uiTheme.colors.border}`,
          background: uiTheme.colors.surface,
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div
          style={{
            maxWidth: 1180,
            margin: "0 auto",
            padding: "12px 16px",
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <div>
              <Link
                to="/"
                style={{
                  fontSize: "1.2rem",
                  fontWeight: 700,
                  color: uiTheme.colors.text,
                  textDecoration: "none",
                }}
              >
                Clínica — Panel
              </Link>
              <div style={{ fontSize: "0.85rem", color: uiTheme.colors.textMuted }}>
                {user?.name} · {user?.role}
              </div>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <Link to="/setup" style={{ fontSize: "0.9rem", color: uiTheme.colors.textMuted }}>
                Setup
              </Link>
              <button type="button" onClick={doLogout} style={uiStyles.buttonSecondary}>
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
            <DistributionNavMenu />
            {isAdmin ? (
              <NavLink to={USERS_NAV_ITEM.path} style={navLinkStyle}>
                {USERS_NAV_ITEM.label}
              </NavLink>
            ) : null}
          </nav>
        </div>
      </header>

      <main style={{ maxWidth: 1180, margin: "0 auto", padding: "22px 16px 40px" }}>
        <Outlet />
      </main>
    </div>
  );
}
