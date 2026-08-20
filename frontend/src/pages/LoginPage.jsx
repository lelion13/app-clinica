import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { apiRequest } from "../services/api";
import { uiStyles, uiTheme } from "../ui/theme";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [forgotOpen, setForgotOpen] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotSubmitting, setForgotSubmitting] = useState(false);
  const [forgotDone, setForgotDone] = useState(false);

  const closeForgot = () => {
    setForgotOpen(false);
    setForgotEmail("");
    setForgotDone(false);
    setForgotSubmitting(false);
  };

  useEffect(() => {
    if (!forgotOpen) return undefined;
    const onKey = (event) => {
      if (event.key === "Escape") closeForgot();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [forgotOpen]);

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const onForgot = async (event) => {
    event.preventDefault();
    setForgotSubmitting(true);
    setError("");
    try {
      await apiRequest("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email: forgotEmail.trim() }),
      });
    } catch {
      // Always show the same message to avoid email enumeration.
    } finally {
      setForgotDone(true);
      setForgotSubmitting(false);
    }
  };

  return (
    <main style={{ maxWidth: 420, margin: "44px auto", display: "grid", gap: 12 }}>
      <section style={uiStyles.pageSection}>
        <h1 style={uiStyles.sectionTitle}>App Clinica - Login</h1>
        <form onSubmit={onSubmit} style={{ display: "grid", gap: 8 }}>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email"
            required
            style={uiStyles.formControl}
          />
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Contrasena"
            required
            style={uiStyles.formControl}
          />
          <button type="submit" disabled={submitting} style={uiStyles.buttonPrimary}>
            {submitting ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
        <button
          type="button"
          onClick={() => {
            setForgotOpen(true);
            setForgotDone(false);
            setForgotEmail(email);
          }}
          style={{
            ...uiStyles.buttonSecondary,
            border: "none",
            background: "transparent",
            padding: 0,
            color: uiTheme.colors.primaryStrong,
            textAlign: "left",
            marginTop: 4,
          }}
        >
          Olvidé mi contraseña
        </button>
        <Link to="/setup" style={{ color: uiTheme.colors.primaryStrong }}>
          Crear admin inicial (solo primer uso)
        </Link>
        {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      </section>

      {forgotOpen ? (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1000,
            background: "rgba(15, 43, 39, 0.45)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            padding: "max(16px, 4vh) 16px",
          }}
          onClick={closeForgot}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="forgot-title"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: uiTheme.radius.md,
              maxWidth: 420,
              width: "100%",
              padding: 22,
              boxShadow: uiTheme.shadow.md,
              border: `1px solid ${uiTheme.colors.border}`,
            }}
          >
            <h2 id="forgot-title" style={{ marginTop: 0, marginBottom: 10, fontSize: "1.1rem" }}>
              Restablecer contraseña
            </h2>
            {forgotDone ? (
              <>
                <p style={{ ...uiStyles.helpText, marginTop: 0 }}>
                  Si el correo está registrado, vas a recibir instrucciones para restablecer la contraseña.
                </p>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <button type="button" style={uiStyles.buttonPrimary} onClick={closeForgot}>
                    Entendido
                  </button>
                </div>
              </>
            ) : (
              <form onSubmit={onForgot} style={{ display: "grid", gap: 10 }}>
                <p style={{ ...uiStyles.helpText, margin: 0 }}>
                  Ingresá tu email. Si está registrado, te enviaremos un enlace.
                </p>
                <input
                  type="email"
                  required
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  placeholder="Email"
                  style={uiStyles.formControl}
                />
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                  <button type="button" style={uiStyles.buttonSecondary} onClick={closeForgot} disabled={forgotSubmitting}>
                    Cancelar
                  </button>
                  <button type="submit" style={uiStyles.buttonPrimary} disabled={forgotSubmitting}>
                    {forgotSubmitting ? "Enviando..." : "Enviar"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      ) : null}
    </main>
  );
}
