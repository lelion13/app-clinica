import { useEffect, useState } from "react";

import { AlertModal } from "../../components/AlertModal";
import { apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

function formatMoney(value) {
  const n = Number(value ?? 0);
  return n.toLocaleString("es-AR", { style: "currency", currency: "ARS" });
}

function formatNumber(value) {
  const n = Number(value ?? 0);
  return n.toLocaleString("es-AR", { maximumFractionDigits: 2 });
}

const thStyle = {
  textAlign: "left",
  padding: "8px 10px",
  borderBottom: `1px solid ${uiTheme.colors.border}`,
  fontSize: 13,
  color: uiTheme.colors.textMuted,
  whiteSpace: "nowrap",
};

const tdStyle = {
  padding: "8px 10px",
  borderBottom: `1px solid ${uiTheme.colors.border}`,
  fontSize: 14,
  verticalAlign: "top",
};

export function NovedadesIndicesPage() {
  const [error, setError] = useState("");
  const [periodos, setPeriodos] = useState([]);
  const [periodoId, setPeriodoId] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  useEffect(() => {
    const boot = async () => {
      setError("");
      try {
        const list = await apiRequestWithRefresh("/novedades/periodos");
        setPeriodos(Array.isArray(list) ? list : []);
      } catch (err) {
        setError(err.message || "No se pudieron cargar los períodos");
      }
    };
    boot();
  }, []);

  useEffect(() => {
    const load = async () => {
      if (!periodoId) {
        setData(null);
        return;
      }
      setLoading(true);
      setError("");
      try {
        const result = await apiRequestWithRefresh(`/novedades/indices?periodo_id=${periodoId}`);
        setData(result);
      } catch (err) {
        setData(null);
        setError(err.message || "No se pudieron cargar los índices");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [periodoId]);

  const porServicio = data?.por_servicio || [];
  const porProfesional = data?.por_profesional || [];

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={uiStyles.pageSection}>
        <h1 style={uiStyles.sectionTitle}>Índices</h1>
        <p style={{ ...uiStyles.helpText, marginBottom: 12 }}>
          Contadores por período: servicio (horas de novedades, monto, profesionales, módulos) y profesional (horas,
          módulos, producción). Solo admin.
        </p>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
          <select
            value={periodoId}
            onChange={(e) => setPeriodoId(e.target.value)}
            style={{ ...uiStyles.formControl, minWidth: 220 }}
          >
            <option value="">Seleccioná período…</option>
            {periodos.map((p) => (
              <option key={p.id} value={p.id}>
                #{p.id} {p.nombre || ""} ({p.estado})
              </option>
            ))}
          </select>
          {loading ? <span style={uiStyles.helpText}>Cargando…</span> : null}
        </div>
      </div>

      <AlertModal open={Boolean(error)} title="Atención" message={error} onClose={() => setError("")} />

      <div style={uiStyles.pageSection}>
        <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Por servicio</h2>
        {!periodoId ? (
          <p style={uiStyles.helpText}>Seleccioná un período para ver métricas.</p>
        ) : !porServicio.length ? (
          <p style={uiStyles.helpText}>Sin actividad de cargas en este período.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 560 }}>
              <thead>
                <tr>
                  <th style={thStyle}>Servicio</th>
                  <th style={thStyle}>Horas (novedades)</th>
                  <th style={thStyle}>Monto</th>
                  <th style={thStyle}>Profesionales</th>
                  <th style={thStyle}>Módulos</th>
                </tr>
              </thead>
              <tbody>
                {porServicio.map((row) => (
                  <tr key={row.servicio_id}>
                    <td style={tdStyle}>{row.servicio_nombre}</td>
                    <td style={tdStyle}>{formatNumber(row.horas)}</td>
                    <td style={tdStyle}>{formatMoney(row.monto)}</td>
                    <td style={tdStyle}>{row.profesionales}</td>
                    <td style={tdStyle}>{row.modulos}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div style={uiStyles.pageSection}>
        <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Por profesional</h2>
        {!periodoId ? (
          <p style={uiStyles.helpText}>Seleccioná un período para ver métricas.</p>
        ) : !porProfesional.length ? (
          <p style={uiStyles.helpText}>Sin actividad en este período.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 640 }}>
              <thead>
                <tr>
                  <th style={thStyle}>Legajo</th>
                  <th style={thStyle}>Profesional</th>
                  <th style={thStyle}>Horas (novedades)</th>
                  <th style={thStyle}>Módulos</th>
                  <th style={thStyle}>Producción (monto)</th>
                  <th style={thStyle}>Producción (cant.)</th>
                </tr>
              </thead>
              <tbody>
                {porProfesional.map((row) => (
                  <tr key={row.professional_id}>
                    <td style={tdStyle}>{row.legajo || "—"}</td>
                    <td style={tdStyle}>{row.professional_name}</td>
                    <td style={tdStyle}>{formatNumber(row.horas)}</td>
                    <td style={tdStyle}>{row.modulos}</td>
                    <td style={tdStyle}>{formatMoney(row.produccion_monto)}</td>
                    <td style={tdStyle}>{row.produccion_cantidad}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
