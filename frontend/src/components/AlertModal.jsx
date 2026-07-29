import { useEffect } from "react";

import { uiStyles, uiTheme } from "../ui/theme";

/**
 * Modal de alerta con un solo botón OK (mensajes de validación / error).
 */
export function AlertModal({ open, title = "Atención", message, onClose }) {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === "Escape" || e.key === "Enter") onClose?.();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open || !message) return null;

  return (
    <div
      role="presentation"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1100,
        background: "rgba(15, 43, 39, 0.45)",
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        padding: "max(16px, 4vh) 16px",
        overflowY: "auto",
      }}
      onClick={onClose}
    >
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="alert-modal-title"
        aria-describedby="alert-modal-message"
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "#fff",
          borderRadius: uiTheme.radius.md,
          maxWidth: 440,
          width: "100%",
          marginBottom: 24,
          padding: 22,
          boxShadow: uiTheme.shadow.md,
          border: `1px solid ${uiTheme.colors.border}`,
        }}
      >
        <h2 id="alert-modal-title" style={{ marginTop: 0, marginBottom: 10, fontSize: "1.1rem", color: uiTheme.colors.text }}>
          {title}
        </h2>
        <p
          id="alert-modal-message"
          style={{ marginTop: 0, marginBottom: 18, color: uiTheme.colors.text, fontSize: 14, lineHeight: 1.45 }}
        >
          {message}
        </p>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button type="button" onClick={onClose} style={uiStyles.buttonPrimary} autoFocus>
            OK
          </button>
        </div>
      </div>
    </div>
  );
}
