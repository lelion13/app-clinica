import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { uiStyles, uiTheme } from "../ui/theme";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

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
        />
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Contrasena"
          required
        />
        <button type="submit" disabled={submitting} style={uiStyles.buttonPrimary}>
          {submitting ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
      <Link to="/setup" style={{ color: uiTheme.colors.primaryStrong }}>Crear admin inicial (solo primer uso)</Link>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      </section>
    </main>
  );
}
