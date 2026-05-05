import { useState } from "react";
import { Link } from "react-router-dom";

import { apiRequest } from "../services/api";
import { uiStyles, uiTheme } from "../ui/theme";

export function SetupPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    setStatus("");
    setSubmitting(true);
    try {
      await apiRequest("/setup/bootstrap-admin", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });
      setStatus("Admin inicial creado. Ya podes iniciar sesion.");
      setName("");
      setEmail("");
      setPassword("");
    } catch (err) {
      setStatus(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main style={{ maxWidth: 520, margin: "44px auto", display: "grid", gap: 12 }}>
      <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Setup inicial</h1>
      <p style={uiStyles.helpText}>Este flujo funciona solo si aun no existe ningun usuario.</p>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: 8 }}>
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Nombre" required />
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
          placeholder="Contrasena (min 8)"
          required
        />
        <button type="submit" disabled={submitting} style={uiStyles.buttonPrimary}>
          {submitting ? "Creando..." : "Crear admin inicial"}
        </button>
      </form>
      <Link to="/login" style={{ color: uiTheme.colors.primaryStrong }}>Volver a login</Link>
      {status ? <p style={{ color: uiTheme.colors.text }}>{status}</p> : null}
      </section>
    </main>
  );
}
