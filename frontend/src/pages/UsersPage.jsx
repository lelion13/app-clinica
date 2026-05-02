import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";

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
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Usuarios</h1>
      <p style={{ color: "#64748b" }}>Alta y baja de cuentas del sistema (solo administradores).</p>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      <form onSubmit={submitUser} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <input value={newUserName} onChange={(event) => setNewUserName(event.target.value)} placeholder="Nombre" required />
        <input
          type="email"
          value={newUserEmail}
          onChange={(event) => setNewUserEmail(event.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={newUserPassword}
          onChange={(event) => setNewUserPassword(event.target.value)}
          placeholder="Contraseña"
          required
        />
        <select value={newUserRole} onChange={(event) => setNewUserRole(event.target.value)}>
          <option value="operador">operador</option>
          <option value="admin">admin</option>
        </select>
        <button type="submit">Crear usuario</button>
      </form>
      <ul style={{ paddingLeft: 20 }}>
        {users.map((item) => (
          <li key={item.id} style={{ marginBottom: 8 }}>
            #{item.id} - {item.name} - {item.email} ({item.role}){" "}
            <button type="button" onClick={() => removeItem(item.id)}>
              eliminar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
