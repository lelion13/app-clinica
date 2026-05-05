import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

export function UsersPage() {
  const [error, setError] = useState("");
  const [users, setUsers] = useState([]);
  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserPassword, setNewUserPassword] = useState("");
  const [newUserRole, setNewUserRole] = useState("operador");

  const load = async () => {
    setError("");
    await safeLoad("/users", setUsers, setError);
  };

  useEffect(() => {
    load();
  }, []);

  const submitUser = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/users", {
      method: "POST",
      body: JSON.stringify({
        name: newUserName,
        email: newUserEmail,
        password: newUserPassword,
        role: newUserRole,
        is_active: true,
      }),
    });
    setNewUserName("");
    setNewUserEmail("");
    setNewUserPassword("");
    setNewUserRole("operador");
    await load();
  };

  const removeItem = async (id) => {
    await apiRequestWithRefresh(`/users/${id}`, { method: "DELETE" });
    await load();
  };

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Usuarios</h1>
      <p style={uiStyles.helpText}>Alta y baja de cuentas del sistema (solo administradores).</p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      <form onSubmit={submitUser} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <input
          value={newUserName}
          onChange={(event) => setNewUserName(event.target.value)}
          placeholder="Nombre"
          required
          style={uiStyles.formControl}
        />
        <input
          type="email"
          value={newUserEmail}
          onChange={(event) => setNewUserEmail(event.target.value)}
          placeholder="Email"
          required
          style={uiStyles.formControl}
        />
        <input
          type="password"
          value={newUserPassword}
          onChange={(event) => setNewUserPassword(event.target.value)}
          placeholder="Contraseña"
          required
          style={uiStyles.formControl}
        />
        <select value={newUserRole} onChange={(event) => setNewUserRole(event.target.value)} style={uiStyles.formControl}>
          <option value="operador">operador</option>
          <option value="admin">admin</option>
        </select>
        <button type="submit" style={uiStyles.buttonPrimary}>Crear usuario</button>
      </form>
      <ul style={uiStyles.listCard}>
        {users.map((item) => (
          <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
            #{item.id} · {item.name} · {item.email} ({item.role}){" "}
            <button type="button" onClick={() => removeItem(item.id)} style={{ ...uiStyles.buttonDanger, marginLeft: 8 }}>
              eliminar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
