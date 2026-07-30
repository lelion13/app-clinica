import { useEffect, useMemo, useState } from "react";

import { apiDownloadWithRefresh, apiRequestWithRefresh } from "../../services/api";
import { AlertModal } from "../../components/AlertModal";
import { uiStyles, uiTheme } from "../../ui/theme";

const thStyle = {
  textAlign: "left",
  padding: "10px 12px",
  borderBottom: `1px solid ${uiTheme.colors.borderStrong}`,
  background: uiTheme.colors.surfaceMuted,
  color: uiTheme.colors.textMuted,
  fontSize: 12,
  fontWeight: 600,
  cursor: "pointer",
  userSelect: "none",
  whiteSpace: "nowrap",
};

const tdStyle = {
  padding: "10px 12px",
  borderBottom: `1px solid ${uiTheme.colors.border}`,
  verticalAlign: "middle",
};

function formatMoney(value) {
  if (value == null || value === "") return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  return `$${n.toLocaleString("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function compareText(a, b) {
  return String(a || "").localeCompare(String(b || ""), "es", { sensitivity: "base" });
}

function compareNumber(a, b) {
  const na = Number(a);
  const nb = Number(b);
  if (Number.isNaN(na) && Number.isNaN(nb)) return 0;
  if (Number.isNaN(na)) return 1;
  if (Number.isNaN(nb)) return -1;
  return na - nb;
}

export function NovedadesXlsPage() {
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [rows, setRows] = useState([]);
  const [servicios, setServicios] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [periodoId, setPeriodoId] = useState("");
  const [servicioId, setServicioId] = useState("");
  const [q, setQ] = useState("");
  const [filterText, setFilterText] = useState("");
  const [sortKey, setSortKey] = useState("professional_name");
  const [sortDir, setSortDir] = useState("asc");

  const [modalRow, setModalRow] = useState(null);
  const [ajustes, setAjustes] = useState([]);
  const [importe, setImporte] = useState("");
  const [comentario, setComentario] = useState("");
  const [saving, setSaving] = useState(false);

  const queryString = () => {
    const params = new URLSearchParams();
    if (periodoId) params.set("periodo_id", periodoId);
    if (servicioId) params.set("servicio_id", servicioId);
    if (q.trim()) params.set("q", q.trim());
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  };

  const load = async () => {
    setError("");
    try {
      const [grid, s, p] = await Promise.all([
        apiRequestWithRefresh(`/novedades/capital-humano${queryString()}`),
        apiRequestWithRefresh("/novedades/servicios"),
        apiRequestWithRefresh("/novedades/periodos"),
      ]);
      setRows(grid);
      setServicios(s);
      setPeriodos(p);
    } catch (err) {
      setError(err.message || "Error al cargar Capital Humano");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const download = async (path, fallbackName) => {
    setError("");
    try {
      const { blob, filename } = await apiDownloadWithRefresh(`${path}${queryString()}`);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename || fallbackName;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "Error al descargar XLS");
    }
  };

  const openModal = async (row) => {
    if (!periodoId) {
      setError("Seleccioná un período para ver o cargar ajustes");
      return;
    }
    setError("");
    setModalRow(row);
    setImporte("");
    setComentario("");
    try {
      const params = new URLSearchParams({
        professional_id: String(row.professional_id),
        periodo_id: periodoId,
      });
      if (servicioId) params.set("servicio_id", servicioId);
      const list = await apiRequestWithRefresh(`/novedades/capital-humano/ajustes?${params}`);
      setAjustes(list);
    } catch (err) {
      setError(err.message || "Error al cargar ajustes");
      setModalRow(null);
    }
  };

  const closeModal = () => {
    if (saving) return;
    setModalRow(null);
    setAjustes([]);
  };

  const submitAjuste = async (event) => {
    event.preventDefault();
    if (!modalRow || !periodoId) return;
    const amount = Number(importe);
    if (!importe.trim() || Number.isNaN(amount) || amount === 0) {
      setError("Ingresá un importe distinto de 0 (positivo suma, negativo resta)");
      return;
    }
    if (!comentario.trim()) {
      setError("El comentario es obligatorio");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await apiRequestWithRefresh("/novedades/capital-humano/ajustes", {
        method: "POST",
        body: JSON.stringify({
          professional_id: modalRow.professional_id,
          periodo_id: Number(periodoId),
          servicio_id: servicioId ? Number(servicioId) : null,
          importe: amount,
          comentario: comentario.trim(),
        }),
      });
      setInfo("Ajuste registrado");
      setImporte("");
      setComentario("");
      await openModal(modalRow);
      await load();
    } catch (err) {
      setError(err.message || "No se pudo guardar el ajuste");
    } finally {
      setSaving(false);
    }
  };

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const sortMark = (key) => (sortKey === key ? (sortDir === "asc" ? " ↑" : " ↓") : "");

  const visibleRows = useMemo(() => {
    const needle = filterText.trim().toLowerCase();
    let list = rows;
    if (needle) {
      list = list.filter((r) => {
        const hay = `${r.legajo || ""} ${r.professional_name || ""}`.toLowerCase();
        return hay.includes(needle);
      });
    }
    const sorted = [...list].sort((a, b) => {
      let cmp = 0;
      if (sortKey === "legajo" || sortKey === "professional_name") {
        cmp = compareText(a[sortKey], b[sortKey]);
      } else {
        cmp = compareNumber(a[sortKey], b[sortKey]);
      }
      return sortDir === "asc" ? cmp : -cmp;
    });
    return sorted;
  }, [rows, filterText, sortKey, sortDir]);

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Capital Humano</h1>
      <p style={uiStyles.helpText}>
        Un registro por profesional: legajo, nombre y monto total (cargas ± ajustes). Los ajustes usan importe con
        signo y comentario obligatorio. Podés descargar la vista agregada o el detalle por carga (formato anterior).
      </p>
      <AlertModal open={Boolean(error)} title="Atención" message={error} onClose={() => setError("")} />
      <AlertModal open={Boolean(info)} title="Listo" message={info} onClose={() => setInfo("")} />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
        <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)} style={uiStyles.formControl}>
          <option value="">Todos los períodos</option>
          {periodos.map((p) => (
            <option key={p.id} value={p.id}>
              #{p.id} {p.nombre || ""} ({p.estado})
            </option>
          ))}
        </select>
        <select value={servicioId} onChange={(e) => setServicioId(e.target.value)} style={uiStyles.formControl}>
          <option value="">Todos los servicios</option>
          {servicios.map((s) => (
            <option key={s.id} value={s.id}>
              {s.nombre}
            </option>
          ))}
        </select>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Buscar en servidor (nombre/legajo)"
          style={uiStyles.formControl}
        />
        <button type="button" style={uiStyles.buttonSecondary} onClick={load}>
          Buscar
        </button>
        <button
          type="button"
          style={uiStyles.buttonPrimary}
          onClick={() => download("/novedades/export-capital.xlsx", "capital-humano.xlsx")}
        >
          Descargar XLS (agregado)
        </button>
        <button
          type="button"
          style={uiStyles.buttonSecondary}
          onClick={() => download("/novedades/export.xlsx", "novedades-detalle.xlsx")}
        >
          Descargar XLS (detalle)
        </button>
      </div>

      <div style={{ marginBottom: 10 }}>
        <input
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          placeholder="Filtrar grilla…"
          style={{ ...uiStyles.formControl, maxWidth: 320 }}
        />
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
          <thead>
            <tr>
              <th style={thStyle} onClick={() => toggleSort("legajo")}>
                Legajo{sortMark("legajo")}
              </th>
              <th style={thStyle} onClick={() => toggleSort("professional_name")}>
                Profesional{sortMark("professional_name")}
              </th>
              <th style={thStyle} onClick={() => toggleSort("monto_cargas")}>
                Cargas{sortMark("monto_cargas")}
              </th>
              <th style={thStyle} onClick={() => toggleSort("monto_ajustes")}>
                Ajustes{sortMark("monto_ajustes")}
              </th>
              <th style={thStyle} onClick={() => toggleSort("monto_total")}>
                Monto total{sortMark("monto_total")}
              </th>
              <th style={{ ...thStyle, cursor: "default" }}>Acción</th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row) => (
              <tr key={row.professional_id}>
                <td style={tdStyle}>{row.legajo || "—"}</td>
                <td style={tdStyle}>{row.professional_name}</td>
                <td style={tdStyle}>{formatMoney(row.monto_cargas)}</td>
                <td style={tdStyle}>
                  <button
                    type="button"
                    onClick={() => openModal(row)}
                    style={{
                      ...uiStyles.buttonSecondary,
                      padding: "4px 10px",
                      fontSize: 13,
                    }}
                    title="Ver historial y agregar ajuste"
                  >
                    {formatMoney(row.monto_ajustes)}
                  </button>
                </td>
                <td style={tdStyle}>{formatMoney(row.monto_total)}</td>
                <td style={tdStyle}>
                  <button type="button" style={uiStyles.buttonPrimary} onClick={() => openModal(row)}>
                    Agregar importe
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!visibleRows.length ? <p style={uiStyles.helpText}>Sin resultados.</p> : null}
      </div>

      {modalRow ? (
        <div
          role="presentation"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1100,
            background: "rgba(15, 43, 39, 0.45)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            padding: "max(16px, 4vh) 16px",
            overflowY: "auto",
          }}
          onClick={closeModal}
        >
          <div
            role="dialog"
            aria-modal="true"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: uiTheme.radius.md,
              maxWidth: 520,
              width: "100%",
              padding: 22,
              boxShadow: uiTheme.shadow.md,
              border: `1px solid ${uiTheme.colors.border}`,
              marginBottom: 24,
            }}
          >
            <h2 style={{ marginTop: 0, marginBottom: 8, fontSize: "1.1rem" }}>
              Ajustes · {modalRow.professional_name}
            </h2>
            <p style={{ ...uiStyles.helpText, marginTop: 0 }}>
              Legajo: {modalRow.legajo || "—"} · Período #{periodoId}
              {servicioId ? ` · Servicio filtrado` : ""}
            </p>

            <form onSubmit={submitAjuste} style={{ display: "grid", gap: 10, marginBottom: 16 }}>
              <label style={{ display: "grid", gap: 4 }}>
                <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>
                  Importe (positivo suma, negativo resta)
                </span>
                <input
                  type="number"
                  step="0.01"
                  value={importe}
                  onChange={(e) => setImporte(e.target.value)}
                  style={uiStyles.formControl}
                  required
                />
              </label>
              <label style={{ display: "grid", gap: 4 }}>
                <span style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>Comentario (obligatorio)</span>
                <textarea
                  value={comentario}
                  onChange={(e) => setComentario(e.target.value)}
                  style={{ ...uiStyles.formControl, minHeight: 72 }}
                  required
                />
              </label>
              <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                <button type="button" style={uiStyles.buttonSecondary} onClick={closeModal} disabled={saving}>
                  Cerrar
                </button>
                <button type="submit" style={uiStyles.buttonPrimary} disabled={saving}>
                  {saving ? "Guardando…" : "Guardar ajuste"}
                </button>
              </div>
            </form>

            <h3 style={{ fontSize: "1rem", marginBottom: 8 }}>Historial</h3>
            <ul style={{ ...uiStyles.listCard, maxHeight: 240, overflowY: "auto" }}>
              {ajustes.map((a) => (
                <li
                  key={a.id}
                  style={{
                    padding: "8px 10px",
                    borderBottom: `1px solid ${uiTheme.colors.border}`,
                    fontSize: 13,
                  }}
                >
                  <strong>{formatMoney(a.importe)}</strong> · {a.comentario}
                  <div style={{ color: uiTheme.colors.textMuted, marginTop: 2 }}>
                    {a.created_by_name || "—"} · {a.created_at ? new Date(a.created_at).toLocaleString("es-AR") : ""}
                  </div>
                </li>
              ))}
              {!ajustes.length ? (
                <li style={{ padding: 10, color: uiTheme.colors.textMuted }}>Sin ajustes en este alcance.</li>
              ) : null}
            </ul>
          </div>
        </div>
      ) : null}
    </section>
  );
}
