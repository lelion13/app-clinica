import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

const ROLES = [
  { value: "operador", label: "operador" },
  { value: "admin", label: "admin" },
  { value: "jefe_medico", label: "jefe_medico" },
  { value: "rrhh", label: "rrhh" },
];

const emptyCreate = () => ({
  name: "",
  email: "",
  password: "",
  role: "operador",
});

const emptyEdit = () => ({
  name: "",
  email: "",
  role: "operador",
  is_active: true,
  password: "",
});

function ModalShell({ titleId, title, onClose, children }) {
  useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
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
        overflowY: "auto",
      }}
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
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
        <h2 id={titleId} style={{ marginTop: 0, marginBottom: 14, fontSize: "1.1rem" }}>
          {title}
        </h2>
        {children}
      </div>
    </div>
  );
}

export function UsersPage() {
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [users, setUsers] = useState([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState(emptyCreate);
  const [createSaving, setCreateSaving] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [editForm, setEditForm] = useState(emptyEdit);
  const [editSaving, setEditSaving] = useState(false);

  const load = async () => {
    setError("");
    await safeLoad("/users", setUsers, setError);
  };

  useEffect(() => {
    load();
  }, []);

  const closeCreate = () => {
    setCreateOpen(false);
    setCreateForm(emptyCreate());
    setCreateSaving(false);
  };

  const closeEdit = () => {
    setEditUser(null);
    setEditForm(emptyEdit());
    setEditSaving(false);
  };

  const openEdit = (user) => {
    setNotice("");
    setError("");
    setEditUser(user);
    setEditForm({
      name: user.name || "",
      email: user.email || "",
      role: user.role || "operador",
      is_active: Boolean(user.is_active),
      password: "",
    });
  };

  const submitCreate = async (event) => {
    event.preventDefault();
    setCreateSaving(true);
    setError("");
    setNotice("");
    try {
      const created = await apiRequestWithRefresh("/users", {
        method: "POST",
        body: JSON.stringify({
          name: createForm.name.trim(),
          email: createForm.email.trim(),
          password: createForm.password,
          role: createForm.role,
          is_active: true,
        }),
      });
      closeCreate();
      if (created?.welcome_email_warning) {
        setNotice(created.welcome_email_warning);
      } else if (created?.welcome_email_sent === false) {
        setNotice("Usuario creado, pero no se pudo enviar el correo de bienvenida");
      } else {
        setNotice("Usuario creado correctamente");
      }
      await load();
    } catch (err) {
      setError(err.message || "No se pudo crear el usuario");
    } finally {
      setCreateSaving(false);
    }
  };

  const submitEdit = async (event) => {
    event.preventDefault();
    if (!editUser) return;
    setEditSaving(true);
    setError("");
    setNotice("");
    try {
      const body = {
        name: editForm.name.trim(),
        email: editForm.email.trim(),
        role: editForm.role,
        is_active: editForm.is_active,
      };
      if (editForm.password.trim()) {
        body.password = editForm.password;
      }
      await apiRequestWithRefresh(`/users/${editUser.id}`, {
        method: "PATCH",
        body: JSON.stringify(body),
      });
      closeEdit();
      setNotice("Usuario actualizado");
      await load();
    } catch (err) {
      setError(err.message || "No se pudo actualizar el usuario");
    } finally {
      setEditSaving(false);
    }
  };

  return (
    <section style={uiStyles.pageSection}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, alignItems: "center", marginBottom: 8 }}>
        <h1 style={{ ...uiStyles.sectionTitle, marginBottom: 0, flex: "1 1 auto" }}>Usuarios</h1>
        <button
          type="button"
          style={uiStyles.buttonPrimary}
          onClick={() => {
            setError("");
            setNotice("");
            setCreateForm(emptyCreate());
            setCreateOpen(true);
          }}
        >
          Nuevo usuario
        </button>
      </div>
      <p style={uiStyles.helpText}>Alta y edición de cuentas (solo administradores). Desactivar un usuario bloquea el login y el restablecimiento de contraseña.</p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      {notice ? <p style={{ color: uiTheme.colors.primaryStrong }}>{notice}</p> : null}

      <div style={{ overflowX: "auto", marginTop: 12 }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem", minWidth: 640 }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
              <th style={{ padding: "8px 10px" }}>Nombre</th>
              <th style={{ padding: "8px 10px" }}>Email</th>
              <th style={{ padding: "8px 10px" }}>Rol</th>
              <th style={{ padding: "8px 10px" }}>Estado</th>
              <th style={{ padding: "8px 10px", textAlign: "right" }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: "12px 10px", color: uiTheme.colors.textMuted }}>
                  No hay usuarios para mostrar.
                </td>
              </tr>
            ) : (
              users.map((item) => (
                <tr key={item.id} style={{ borderBottom: `1px solid ${uiTheme.colors.border}` }}>
                  <td style={{ padding: "8px 10px" }}>{item.name}</td>
                  <td style={{ padding: "8px 10px" }}>{item.email}</td>
                  <td style={{ padding: "8px 10px" }}>{item.role}</td>
                  <td style={{ padding: "8px 10px" }}>{item.is_active ? "Activo" : "Inactivo"}</td>
                  <td style={{ padding: "8px 10px", textAlign: "right" }}>
                    <button type="button" style={uiStyles.buttonSecondary} onClick={() => openEdit(item)}>
                      Modificar
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {createOpen ? (
        <ModalShell titleId="user-create-title" title="Nuevo usuario" onClose={closeCreate}>
          <form onSubmit={submitCreate} style={{ display: "grid", gap: 10 }}>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Nombre y apellido</span>
              <input
                required
                value={createForm.name}
                onChange={(e) => setCreateForm((f) => ({ ...f, name: e.target.value }))}
                style={uiStyles.formControl}
              />
            </label>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Email (usuario de login)</span>
              <input
                required
                type="email"
                value={createForm.email}
                onChange={(e) => setCreateForm((f) => ({ ...f, email: e.target.value }))}
                style={uiStyles.formControl}
              />
            </label>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Contraseña</span>
              <input
                required
                type="password"
                minLength={8}
                value={createForm.password}
                onChange={(e) => setCreateForm((f) => ({ ...f, password: e.target.value }))}
                style={uiStyles.formControl}
              />
            </label>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Rol</span>
              <select
                value={createForm.role}
                onChange={(e) => setCreateForm((f) => ({ ...f, role: e.target.value }))}
                style={uiStyles.formControl}
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </label>
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 6 }}>
              <button type="button" style={uiStyles.buttonSecondary} onClick={closeCreate} disabled={createSaving}>
                Cancelar
              </button>
              <button type="submit" style={uiStyles.buttonPrimary} disabled={createSaving}>
                {createSaving ? "Creando..." : "Crear"}
              </button>
            </div>
          </form>
        </ModalShell>
      ) : null}

      {editUser ? (
        <ModalShell titleId="user-edit-title" title="Modificar usuario" onClose={closeEdit}>
          <form onSubmit={submitEdit} style={{ display: "grid", gap: 10 }}>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Nombre y apellido</span>
              <input
                required
                value={editForm.name}
                onChange={(e) => setEditForm((f) => ({ ...f, name: e.target.value }))}
                style={uiStyles.formControl}
              />
            </label>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Email (usuario de login)</span>
              <input
                required
                type="email"
                value={editForm.email}
                onChange={(e) => setEditForm((f) => ({ ...f, email: e.target.value }))}
                style={uiStyles.formControl}
              />
            </label>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Rol</span>
              <select
                value={editForm.role}
                onChange={(e) => setEditForm((f) => ({ ...f, role: e.target.value }))}
                style={uiStyles.formControl}
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </label>
            <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <input
                type="checkbox"
                checked={editForm.is_active}
                onChange={(e) => setEditForm((f) => ({ ...f, is_active: e.target.checked }))}
              />
              <span style={{ fontSize: 14 }}>Usuario activo</span>
            </label>
            <label style={{ display: "grid", gap: 4 }}>
              <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>
                Nueva contraseña (opcional)
              </span>
              <input
                type="password"
                minLength={8}
                value={editForm.password}
                onChange={(e) => setEditForm((f) => ({ ...f, password: e.target.value }))}
                style={uiStyles.formControl}
                placeholder="Dejar vacío para no cambiar"
              />
            </label>
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 6 }}>
              <button type="button" style={uiStyles.buttonSecondary} onClick={closeEdit} disabled={editSaving}>
                Cancelar
              </button>
              <button type="submit" style={uiStyles.buttonPrimary} disabled={editSaving}>
                {editSaving ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </form>
        </ModalShell>
      ) : null}
    </section>
  );
}
