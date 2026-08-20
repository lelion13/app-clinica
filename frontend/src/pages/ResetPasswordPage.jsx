import { useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { apiRequest } from "../services/api";
import { uiStyles, uiTheme } from "../ui/theme";

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const token = useMemo(() => (params.get("token") || "").trim(), [params]);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (!token) {
      setError("El enlace no es válido o expiró");
      return;
    }
    if (password !== confirm) {
      setError("Las contraseñas no coinciden");
      return;
    }
    setSubmitting(true);
    try {
      await apiRequest("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ token, password }),
      });
      setDone(true);
    } catch (err) {
      setError(err.message || "El enlace no es válido o expiró");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main style={{ maxWidth: 420, margin: "44px auto", display: "grid", gap: 12 }}>
      <section style={uiStyles.pageSection}>
        <h1 style={uiStyles.sectionTitle}>Nueva contraseña</h1>
        {done ? (
          <>
            <p style={uiStyles.helpText}>Tu contraseña se actualizó. Ya podés ingresar.</p>
            <button type="button" style={uiStyles.buttonPrimary} onClick={() => navigate("/login", { replace: true })}>
              Ir al login
            </button>
          </>
        ) : (
          <form onSubmit={onSubmit} style={{ display: "grid", gap: 8 }}>
            {!token ? (
              <p style={{ color: uiTheme.colors.danger, margin: 0 }}>El enlace no es válido o expiró.</p>
            ) : null}
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nueva contraseña"
              minLength={8}
              required
              style={uiStyles.formControl}
            />
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              placeholder="Repetir contraseña"
              minLength={8}
              required
              style={uiStyles.formControl}
            />
            <button type="submit" disabled={submitting || !token} style={uiStyles.buttonPrimary}>
              {submitting ? "Guardando..." : "Guardar contraseña"}
            </button>
          </form>
        )}
        <Link to="/login" style={{ color: uiTheme.colors.primaryStrong }}>
          Volver al login
        </Link>
        {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      </section>
    </main>
  );
}
