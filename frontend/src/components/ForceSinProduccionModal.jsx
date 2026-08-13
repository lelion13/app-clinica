import { useEffect, useState } from "react";

import { uiStyles, uiTheme } from "../ui/theme";

const MOTIVO_OPTIONS = [
  { value: "vacaciones", label: "Vacaciones" },
  { value: "enfermedad", label: "Enfermedad" },
];

/**
 * Modal when create is blocked by sin producción: motivo + observación + Cancelar/Cargar.
 */
export function ForceSinProduccionModal({ open, message, loading, onCancel, onConfirm }) {
  const [motivo, setMotivo] = useState("");
  const [observacion, setObservacion] = useState("");
  const [localError, setLocalError] = useState("");

  useEffect(() => {
    if (!open) return;
    setMotivo("");
    setObservacion("");
    setLocalError("");
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === "Escape" && !loading) onCancel?.();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, loading, onCancel]);

  if (!open) return null;

  const handleConfirm = () => {
    const motivoVal = (motivo || "").trim();
    const obsVal = (observacion || "").trim();
    if (!motivoVal) {
      setLocalError("Seleccioná un motivo");
      return;
    }
    if (!obsVal) {
      setLocalError("La observación es obligatoria");
      return;
    }
    setLocalError("");
    onConfirm?.({ motivo_sin_produccion: motivoVal, observacion_sin_produccion: obsVal });
  };

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
      onClick={() => {
        if (!loading) onCancel?.();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="force-sin-prod-title"
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "#fff",
          borderRadius: uiTheme.radius.md,
          maxWidth: 480,
          width: "100%",
          marginBottom: 24,
          padding: 22,
          boxShadow: uiTheme.shadow.md,
          border: `1px solid ${uiTheme.colors.border}`,
        }}
      >
        <h2 id="force-sin-prod-title" style={{ marginTop: 0, marginBottom: 10, fontSize: "1.1rem" }}>
          Sin producción
        </h2>
        <p style={{ marginTop: 0, marginBottom: 14, color: uiTheme.colors.text, fontSize: 14, lineHeight: 1.45 }}>
          {message}
        </p>
        <label style={{ display: "grid", gap: 4, marginBottom: 10 }}>
          <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Motivo</span>
          <select
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            style={uiStyles.formControl}
            disabled={loading}
          >
            <option value="">Elegí motivo</option>
            {MOTIVO_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "grid", gap: 4, marginBottom: 12 }}>
          <span style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Observación</span>
          <textarea
            value={observacion}
            onChange={(e) => setObservacion(e.target.value)}
            rows={3}
            maxLength={500}
            placeholder="Obligatoria"
            style={{ ...uiStyles.formControl, resize: "vertical", minHeight: 72 }}
            disabled={loading}
          />
        </label>
        {localError ? (
          <p style={{ color: uiTheme.colors.danger, margin: "0 0 10px", fontSize: 14 }}>{localError}</p>
        ) : null}
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", flexWrap: "wrap" }}>
          <button type="button" onClick={onCancel} style={uiStyles.buttonSecondary} disabled={loading}>
            Cancelar
          </button>
          <button type="button" onClick={handleConfirm} style={uiStyles.buttonPrimary} disabled={loading}>
            {loading ? "Cargando…" : "Cargar"}
          </button>
        </div>
      </div>
    </div>
  );
}
