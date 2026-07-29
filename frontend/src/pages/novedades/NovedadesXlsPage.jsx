import { useEffect, useState } from "react";

import { apiDownloadWithRefresh, apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

export function NovedadesXlsPage() {
  const [error, setError] = useState("");
  const [rows, setRows] = useState([]);
  const [servicios, setServicios] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [periodoId, setPeriodoId] = useState("");
  const [servicioId, setServicioId] = useState("");
  const [q, setQ] = useState("");
  const [concepto, setConcepto] = useState("");

  const queryString = () => {
    const params = new URLSearchParams();
    if (periodoId) params.set("periodo_id", periodoId);
    if (servicioId) params.set("servicio_id", servicioId);
    if (q.trim()) params.set("q", q.trim());
    if (concepto.trim()) params.set("concepto", concepto.trim());
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  };

  const load = async () => {
    setError("");
    try {
      const [grid, s, p] = await Promise.all([
        apiRequestWithRefresh(`/novedades/grilla${queryString()}`),
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/periodos"),
      ]);
      setRows(grid);
      setServicios(s);
      setPeriodos(p);
    } catch (err) {
      setError(err.message || "Error al cargar grilla");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const download = async () => {
    setError("");
    try {
      const { blob, filename } = await apiDownloadWithRefresh(`/novedades/export.xlsx${queryString()}`);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "Error al descargar XLS");
    }
  };

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Generación archivo XLS</h1>
      <p style={uiStyles.helpText}>
        Grilla de módulos asignados y novedades. En novedades, valor = horas × valor hora.
      </p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
        <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)} style={uiStyles.formControl}>
          <option value="">Todos los períodos</option>
          {periodos.map((p) => (
            <option key={p.id} value={p.id}>#{p.id} {p.nombre || ""} ({p.estado})</option>
          ))}
        </select>
        <select value={servicioId} onChange={(e) => setServicioId(e.target.value)} style={uiStyles.formControl}>
          <option value="">Todos los servicios</option>
          {servicios.map((s) => (
            <option key={s.id} value={s.id}>{s.nombre}</option>
          ))}
        </select>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar profesional/servicio" style={uiStyles.formControl} />
        <input value={concepto} onChange={(e) => setConcepto(e.target.value)} placeholder="Concepto / tipo" style={uiStyles.formControl} />
        <button type="button" style={uiStyles.buttonSecondary} onClick={load}>Buscar</button>
        <button type="button" style={uiStyles.buttonPrimary} onClick={download}>Descargar XLS</button>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
          <thead>
            <tr>
              {["Período", "Servicio", "Profesional", "Tipo", "Concepto", "Horas", "Valor hora", "Valor", "Cargado por", "F. realización", "Fecha carga"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.tipo}-${row.id}`}>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.periodo_nombre || row.periodo_id}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.servicio_nombre}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.professional_name}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.tipo}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.concepto}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.horas ?? "—"}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.valor_hora ?? "—"}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.valor ?? "—"}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.cargado_por || "—"}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.fecha_realizacion || "—"}</td>
                <td style={{ padding: 8, borderBottom: `1px solid ${uiTheme.colors.border}` }}>{row.fecha_carga}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!rows.length ? <p style={uiStyles.helpText}>Sin resultados.</p> : null}
      </div>
    </section>
  );
}
