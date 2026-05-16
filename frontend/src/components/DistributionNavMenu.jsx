import { useEffect, useId, useRef, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { DISTRIBUTION_ITEMS, isDistributionPath, itemsForRole } from "../config/navigation";
import { navPillStyle, uiTheme } from "../ui/theme";

const submenuLinkStyle = ({ isActive }) => ({
  display: "block",
  padding: "10px 14px",
  textDecoration: "none",
  color: isActive ? uiTheme.colors.primaryStrong : uiTheme.colors.text,
  background: isActive ? uiTheme.colors.primarySoft : "transparent",
  fontWeight: isActive ? 600 : 500,
  fontSize: "0.9rem",
});

export function DistributionNavMenu() {
  const { user } = useAuth();
  const location = useLocation();
  const menuId = useId();
  const rootRef = useRef(null);
  const [open, setOpen] = useState(false);

  const visibleItems = itemsForRole(DISTRIBUTION_ITEMS, user?.role);
  const parentActive = isDistributionPath(location.pathname);

  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const onPointerDown = (event) => {
      if (!rootRef.current?.contains(event.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, []);

  return (
    <div ref={rootRef} style={{ position: "relative" }}>
      <button
        type="button"
        id={`${menuId}-trigger`}
        aria-haspopup="true"
        aria-expanded={open}
        aria-controls={`${menuId}-menu`}
        onClick={() => setOpen((value) => !value)}
        style={{
          ...navPillStyle(parentActive),
          cursor: "pointer",
          fontFamily: "inherit",
        }}
      >
        Distribución de consultorios
      </button>

      {open ? (
        <div
          id={`${menuId}-menu`}
          role="menu"
          aria-labelledby={`${menuId}-trigger`}
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            left: 0,
            minWidth: 220,
            zIndex: 20,
            border: `1px solid ${uiTheme.colors.border}`,
            borderRadius: uiTheme.radius.md,
            background: uiTheme.colors.surface,
            boxShadow: uiTheme.shadow.md,
            overflow: "hidden",
          }}
        >
          {visibleItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              role="menuitem"
              style={submenuLinkStyle}
              onClick={() => setOpen(false)}
            >
              {item.label}
            </NavLink>
          ))}
        </div>
      ) : null}
    </div>
  );
}
