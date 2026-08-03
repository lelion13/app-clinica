import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { uiStyles, uiTheme } from "../ui/theme";

const COLUMNS = [
  { key: "id_dominio", label: "id_dominio" },
  { key: "tipo", label: "tipo" },
  { key: "especialidad_agenda", label: "especialidad_agenda" },
  { key: "medico", label: "medico" },
  { key: "especialidad", label: "especialidad" },
  { key: "dia", label: "dia" },
  { key: "fecha_desde", label: "fecha_desde" },
  { key: "hora_desde", label: "hora_desde" },
  { key: "fecha_hasta", label: "fecha_hasta" },
  { key: "hora_hasta", label: "hora_hasta" },
  { key: "duracion_turno", label: "duracion_turno" },
];

const thStyle = {
  textAlign: "left",
  padding: "8px 10px",
  borderBottom: `1px solid ${uiTheme.colors.borderStrong}`,
  background: uiTheme.colors.surfaceMuted,
  color: uiTheme.colors.textMuted,
  fontWeight: 600,
  whiteSpace: "nowrap",
};

const tdStyle = {
  padding: "8px 10px",
  borderBottom: `1px solid ${uiTheme.colors.border}`,
  color: uiTheme.colors.text,
  verticalAlign: "top",
};

export function OccupancyPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [items, setItems] = useState([]);

  const load = async () => {
    setError("");
    setLoading(true);
    try {
      const data = await apiRequestWithRefresh("/distribucion/ocupacion/horarios-activos");
      setItems(Array.isArray(data?.items) ? data.items : []);
    } catch (err) {
      setItems([]);
      setError(err.message || "No se pudieron cargar los horarios activos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <section style={uiStyles.pageSection}>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 12,
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 8,
        }}
      >
        <h1 style={{ ...uiStyles.sectionTitle, marginBottom: 0 }}>Ocupación</h1>
        <button type="button" onClick={load} disabled={loading} style={uiStyles.buttonSecondary}>
          {loading ? "Cargando..." : "Actualizar"}
        </button>
      </div>
      <p style={uiStyles.helpText}>Horarios activos desde la API externa (vista inicial).</p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      {!error && !loading && items.length === 0 ? (
        <p style={uiStyles.helpText}>No hay horarios activos para mostrar.</p>
      ) : null}
      <div
        style={{
          overflowX: "auto",
          marginTop: 12,
          border: `1px solid ${uiTheme.colors.border}`,
          borderRadius: uiTheme.radius.md,
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem", minWidth: 720 }}>
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th key={col.key} style={thStyle}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((row, index) => (
              <tr key={row.id_dato || row.id || `row-${index}`}>
                {COLUMNS.map((col) => (
                  <td key={col.key} style={tdStyle}>
                    {row[col.key] ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
