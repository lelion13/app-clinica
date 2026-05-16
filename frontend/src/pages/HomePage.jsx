import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import {
  DISTRIBUTION_ITEMS,
  USERS_NAV_ITEM,
  canAccessModule,
  itemsForRole,
} from "../config/navigation";
import { uiStyles, uiTheme } from "../ui/theme";

const cardLinkStyle = {
  display: "block",
  padding: "14px 16px",
  borderRadius: uiTheme.radius.md,
  border: `1px solid ${uiTheme.colors.border}`,
  background: uiTheme.colors.surfaceMuted,
  textDecoration: "none",
  color: uiTheme.colors.text,
  fontWeight: 600,
  fontSize: "0.95rem",
  transition: "border-color 160ms ease, background-color 160ms ease",
};

export function HomePage() {
  const { user, isAdmin } = useAuth();
  const distributionLinks = itemsForRole(DISTRIBUTION_ITEMS, user?.role);
  const showUsers = isAdmin && canAccessModule(user?.role, USERS_NAV_ITEM.roles);

  return (
    <section style={{ display: "grid", gap: 20 }}>
      <div style={uiStyles.pageSection}>
        <h1 style={uiStyles.sectionTitle}>Bienvenido{user?.name ? `, ${user.name}` : ""}</h1>
        <p style={{ ...uiStyles.helpText, marginBottom: 0 }}>
          Panel de la clínica. Elegí un módulo desde el menú superior o los accesos rápidos.
        </p>
      </div>

      <div style={{ display: "grid", gap: 12 }}>
        <h2 style={{ margin: 0, fontSize: "1.05rem", color: uiTheme.colors.text }}>Distribución de consultorios</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
            gap: 10,
          }}
        >
          {distributionLinks.map((item) => (
            <Link key={item.path} to={item.path} style={cardLinkStyle}>
              {item.label}
            </Link>
          ))}
        </div>
      </div>

      {showUsers ? (
        <div style={{ display: "grid", gap: 12 }}>
          <h2 style={{ margin: 0, fontSize: "1.05rem", color: uiTheme.colors.text }}>Administración</h2>
          <Link to={USERS_NAV_ITEM.path} style={{ ...cardLinkStyle, maxWidth: 280 }}>
            {USERS_NAV_ITEM.label}
          </Link>
        </div>
      ) : null}
    </section>
  );
}
