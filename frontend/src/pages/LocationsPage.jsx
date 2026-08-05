import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

export function LocationsPage() {
  const [error, setError] = useState("");
  const [locations, setLocations] = useState([]);
  const [locationName, setLocationName] = useState("");
  const [idDominio, setIdDominio] = useState("");
  const [tipo, setTipo] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState("");
  const [editIdDominio, setEditIdDominio] = useState("");
  const [editTipo, setEditTipo] = useState("");
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setError("");
    await safeLoad("/locations", setLocations, setError);
  };

  useEffect(() => {
    load();
  }, []);

  const submitLocation = async (event) => {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      await apiRequestWithRefresh("/locations", {
        method: "POST",
        body: JSON.stringify({
          name: locationName,
          id_dominio: Number(idDominio),
          tipo: tipo.trim(),
        }),
      });
      setLocationName("");
      setIdDominio("");
      setTipo("");
      await load();
    } catch (err) {
      setError(err.message || "No se pudo crear la ubicacion");
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setEditName(item.name || "");
    setEditIdDominio(String(item.id_dominio ?? ""));
    setEditTipo(item.tipo || "");
    setError("");
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditName("");
    setEditIdDominio("");
    setEditTipo("");
  };

  const saveEdit = async (event) => {
    event.preventDefault();
    if (!editingId) return;
    setError("");
    setSaving(true);
    try {
      await apiRequestWithRefresh(`/locations/${editingId}`, {
        method: "PUT",
        body: JSON.stringify({
          name: editName,
          id_dominio: Number(editIdDominio),
          tipo: editTipo.trim(),
        }),
      });
      cancelEdit();
      await load();
    } catch (err) {
      setError(err.message || "No se pudo actualizar la ubicacion");
    } finally {
      setSaving(false);
    }
  };

  const removeItem = async (id) => {
    setError("");
    try {
      await apiRequestWithRefresh(`/locations/${id}`, { method: "DELETE" });
      if (editingId === id) cancelEdit();
      await load();
    } catch (err) {
      setError(err.message || "No se pudo eliminar la ubicacion");
    }
  };

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Ubicaciones</h1>
      <p style={uiStyles.helpText}>
        Sedes o puntos físicos donde hay consultorios. El par <strong>id_dominio</strong> +{" "}
        <strong>tipo</strong> vincula la sede con Ocupación (mismo código y tipo del endpoint externo). El
        tipo es obligatorio y debe coincidir con el valor de ocupación (ej. SEDE TORRE).
      </p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      <form onSubmit={submitLocation} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <input
          value={locationName}
          onChange={(event) => setLocationName(event.target.value)}
          placeholder="Nombre"
          required
          style={{ ...uiStyles.formControl, minWidth: 220 }}
        />
        <input
          type="number"
          min={1}
          step={1}
          value={idDominio}
          onChange={(event) => setIdDominio(event.target.value)}
          placeholder="id_dominio"
          required
          style={{ ...uiStyles.formControl, width: 140 }}
        />
        <input
          value={tipo}
          onChange={(event) => setTipo(event.target.value)}
          placeholder="tipo (ej. SEDE TORRE)"
          required
          style={{ ...uiStyles.formControl, minWidth: 180 }}
        />
        <button type="submit" disabled={saving} style={uiStyles.buttonPrimary}>
          Agregar
        </button>
      </form>
      <ul style={uiStyles.listCard}>
        {locations.map((item) => (
          <li key={item.id} style={{ padding: "10px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
            {editingId === item.id ? (
              <form onSubmit={saveEdit} style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                <span style={{ color: uiTheme.colors.textMuted }}>#{item.id}</span>
                <input
                  value={editName}
                  onChange={(event) => setEditName(event.target.value)}
                  required
                  style={{ ...uiStyles.formControl, minWidth: 180 }}
                />
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={editIdDominio}
                  onChange={(event) => setEditIdDominio(event.target.value)}
                  required
                  style={{ ...uiStyles.formControl, width: 140 }}
                />
                <input
                  value={editTipo}
                  onChange={(event) => setEditTipo(event.target.value)}
                  placeholder="tipo"
                  required
                  style={{ ...uiStyles.formControl, minWidth: 160 }}
                />
                <button type="submit" disabled={saving} style={uiStyles.buttonPrimary}>
                  Guardar
                </button>
                <button type="button" onClick={cancelEdit} style={uiStyles.buttonSecondary}>
                  Cancelar
                </button>
              </form>
            ) : (
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                <span>
                  #{item.id} — {item.name}{" "}
                  <span style={{ color: uiTheme.colors.textMuted }}>
                    (id_dominio: {item.id_dominio}
                    {item.id_dominio < 0 ? " · pendiente" : ""}
                    {" · tipo: "}
                    {item.tipo || "—"}
                    {item.tipo?.startsWith?.("PENDIENTE-") ? " · pendiente" : ""})
                  </span>
                </span>
                <button type="button" onClick={() => startEdit(item)} style={uiStyles.buttonSecondary}>
                  editar
                </button>
                <button type="button" onClick={() => removeItem(item.id)} style={uiStyles.buttonDanger}>
                  eliminar
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
