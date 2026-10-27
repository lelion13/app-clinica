import { Fragment, useCallback, useEffect, useState } from "react";

import { AlertModal } from "../../components/AlertModal";
import { apiDownloadWithRefresh, apiRequestWithRefresh } from "../../services/api";
import { uiStyles, uiTheme } from "../../ui/theme";

function formatMoney(value) {
  const n = Number(value ?? 0);
  return n.toLocaleString("es-AR", { style: "currency", currency: "ARS" });
}

function formatNumber(value) {
  const n = Number(value ?? 0);
  return n.toLocaleString("es-AR", { maximumFractionDigits: 2 });
}

function formatDate(value) {
  if (!value) return "—";
  try {
    return new Date(`${value}T12:00:00`).toLocaleDateString("es-AR");
  } catch {
    return String(value);
  }
}

const FILTRO_OPTIONS = [
  { value: "ambos", label: "Ambos" },
  { value: "modulos", label: "Módulos" },
  { value: "novedades", label: "Novedades" },
  { value: "novedad_extra", label: "Novedad extra" },
];

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

const thDetail = { ...thStyle, fontSize: 12, padding: "6px 8px" };
const tdDetail = { ...tdStyle, fontSize: 13, padding: "6px 8px" };

export function NovedadesIndicesPage() {
  const [error, setError] = useState("");
  const [periodos, setPeriodos] = useState([]);
  const [periodoId, setPeriodoId] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  const [extrasOpen, setExtrasOpen] = useState(false);
  const [extrasFiltro, setExtrasFiltro] = useState("ambos");
  const [extrasQ, setExtrasQ] = useState("");
  const [extrasQApplied, setExtrasQApplied] = useState("");
  const [extrasLoading, setExtrasLoading] = useState(false);
  const [extrasData, setExtrasData] = useState(null);
  const [expanded, setExpanded] = useState(() => new Set());
  const [selected, setSelected] = useState(() => new Set());
  const [exporting, setExporting] = useState(false);

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

  const loadExtras = useCallback(async () => {
    if (!periodoId) return;
    setExtrasLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({
        periodo_id: String(periodoId),
        filtro: extrasFiltro,
      });
      if (extrasQApplied.trim()) params.set("q", extrasQApplied.trim());
      const result = await apiRequestWithRefresh(`/novedades/indices/valores-extras?${params}`);
      setExtrasData(result);
      setExpanded(new Set());
      setSelected(new Set());
    } catch (err) {
      setExtrasData(null);
      setError(err.message || "No se pudieron cargar Valores Extras");
    } finally {
      setExtrasLoading(false);
    }
  }, [periodoId, extrasFiltro, extrasQApplied]);

  useEffect(() => {
    if (!extrasOpen || !periodoId) return;
    loadExtras();
  }, [extrasOpen, periodoId, loadExtras]);

  const openExtras = () => {
    if (!periodoId) return;
    setExtrasFiltro("ambos");
    setExtrasQ("");
    setExtrasQApplied("");
    setExtrasData(null);
    setExpanded(new Set());
    setSelected(new Set());
    setExtrasOpen(true);
  };

  const closeExtras = () => {
    setExtrasOpen(false);
  };

  const toggleExpand = (pid) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(pid)) next.delete(pid);
      else next.add(pid);
      return next;
    });
  };

  const toggleSelect = (pid) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(pid)) next.delete(pid);
      else next.add(pid);
      return next;
    });
  };

  const applySearch = (e) => {
    e.preventDefault();
    setExtrasQApplied(extrasQ);
  };

  const porServicio = data?.por_servicio || [];
  const porProfesional = data?.por_profesional || [];
  const extrasRows = extrasData?.profesionales || [];
  const allSelected = extrasRows.length > 0 && extrasRows.every((r) => selected.has(r.professional_id));
  const someSelected = extrasRows.some((r) => selected.has(r.professional_id));
  const periodoLabel =
    periodos.find((p) => String(p.id) === String(periodoId))?.nombre ||
    (periodoId ? `#${periodoId}` : "");

  const toggleSelectAll = () => {
    if (allSelected) {
      setSelected(new Set());
      return;
    }
    setSelected(new Set(extrasRows.map((r) => r.professional_id)));
  };

  const exportPdf = async () => {
    if (!periodoId || !selected.size) {
      setError("Seleccioná al menos un profesional para exportar");
      return;
    }
    setExporting(true);
    setError("");
    try {
      const { blob, filename } = await apiDownloadWithRefresh("/novedades/indices/valores-extras/pdf", {
        method: "POST",
        body: {
          periodo_id: Number(periodoId),
          filtro: extrasFiltro,
          q: extrasQApplied.trim() || null,
          professional_ids: Array.from(selected),
        },
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename || "Valores_Extras.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "No se pudo exportar el PDF");
    } finally {
      setExporting(false);
    }
  };

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={uiStyles.pageSection}>
        <h1 style={uiStyles.sectionTitle}>Índices</h1>
        <p style={{ ...uiStyles.helpText, marginBottom: 12 }}>
          Contadores por período: servicio (horas = módulos + novedades, monto, profesionales, módulos) y profesional
          (mismas horas, módulos, producción). Solo admin.
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
          <button
            type="button"
            style={uiStyles.buttonSecondary}
            disabled={!periodoId || loading}
            onClick={openExtras}
          >
            Valores Extras
          </button>
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
                  <th style={thStyle}>Horas</th>
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
                  <th style={thStyle}>Horas</th>
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

      {extrasOpen ? (
        <div
          role="presentation"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1000,
            background: "rgba(15, 43, 39, 0.45)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            padding: "max(12px, 3vh) 12px",
            overflowY: "auto",
          }}
          onClick={closeExtras}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="valores-extras-title"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: uiTheme.radius.md,
              maxWidth: 1100,
              width: "100%",
              marginBottom: 24,
              padding: 20,
              boxShadow: uiTheme.shadow.md,
              border: `1px solid ${uiTheme.colors.border}`,
              maxHeight: "92vh",
              overflow: "auto",
            }}
          >
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: 10,
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: 12,
              }}
            >
              <div>
                <h2 id="valores-extras-title" style={{ margin: 0, fontSize: "1.15rem" }}>
                  Valores Extras
                </h2>
                <p style={{ ...uiStyles.helpText, margin: "4px 0 0" }}>
                  Período: {periodoLabel}. Cargas del período (control).
                </p>
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <button
                  type="button"
                  style={uiStyles.buttonPrimary}
                  onClick={exportPdf}
                  disabled={exporting || !someSelected || extrasLoading}
                >
                  {exporting ? "Exportando…" : "Exportar"}
                </button>
                <button type="button" style={uiStyles.buttonSecondary} onClick={closeExtras}>
                  Cerrar
                </button>
              </div>
            </div>

            <form
              onSubmit={applySearch}
              style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center", marginBottom: 14 }}
            >
              <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 13 }}>
                Tipo
                <select
                  value={extrasFiltro}
                  onChange={(e) => setExtrasFiltro(e.target.value)}
                  style={{ ...uiStyles.formControl, minWidth: 160 }}
                >
                  {FILTRO_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </label>
              <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 13, flex: "1 1 180px" }}>
                Profesional
                <input
                  value={extrasQ}
                  onChange={(e) => setExtrasQ(e.target.value)}
                  placeholder="Nombre o legajo…"
                  style={uiStyles.formControl}
                />
              </label>
              <button type="submit" style={{ ...uiStyles.buttonPrimary, alignSelf: "flex-end" }} disabled={extrasLoading}>
                Buscar
              </button>
              {extrasLoading ? <span style={{ ...uiStyles.helpText, alignSelf: "flex-end" }}>Cargando…</span> : null}
            </form>

            {!extrasRows.length && !extrasLoading ? (
              <p style={uiStyles.helpText}>Sin cargas para el filtro.</p>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 760 }}>
                  <thead>
                    <tr>
                      <th style={thStyle}>
                        <input
                          type="checkbox"
                          checked={allSelected}
                          onChange={toggleSelectAll}
                          disabled={!extrasRows.length}
                          aria-label="Seleccionar todos"
                          title="Seleccionar todos"
                        />
                      </th>
                      <th style={thStyle} />
                      <th style={thStyle}>Legajo</th>
                      <th style={thStyle}>Profesional</th>
                      <th style={thStyle}>Cant. mód.</th>
                      <th style={thStyle}>Cant. nov.</th>
                      <th style={thStyle}>Imp. mód.</th>
                      <th style={thStyle}>Imp. nov.</th>
                      <th style={thStyle}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {extrasRows.map((row) => {
                      const open = expanded.has(row.professional_id);
                      const isChecked = selected.has(row.professional_id);
                      return (
                        <Fragment key={row.professional_id}>
                          <tr>
                            <td style={tdStyle}>
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => toggleSelect(row.professional_id)}
                                aria-label={`Seleccionar ${row.professional_name}`}
                              />
                            </td>
                            <td style={tdStyle}>
                              <button
                                type="button"
                                style={{ ...uiStyles.buttonSecondary, padding: "4px 8px", fontSize: 12 }}
                                onClick={() => toggleExpand(row.professional_id)}
                                aria-expanded={open}
                              >
                                {open ? "−" : "+"}
                              </button>
                            </td>
                            <td style={tdStyle}>{row.legajo || "—"}</td>
                            <td style={tdStyle}>{row.professional_name}</td>
                            <td style={tdStyle}>{row.cant_modulos}</td>
                            <td style={tdStyle}>{row.cant_novedades}</td>
                            <td style={tdStyle}>{formatMoney(row.importe_modulos)}</td>
                            <td style={tdStyle}>{formatMoney(row.importe_novedades)}</td>
                            <td style={tdStyle}>{formatMoney(row.importe_total)}</td>
                          </tr>
                          {open ? (
                            <tr>
                              <td style={{ ...tdStyle, borderBottom: "none" }} colSpan={9}>
                                <div
                                  style={{
                                    overflowX: "auto",
                                    background: "#f7faf9",
                                    borderRadius: 8,
                                    padding: 8,
                                  }}
                                >
                                  <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 900 }}>
                                    <thead>
                                      <tr>
                                        <th style={thDetail}>Fecha</th>
                                        <th style={thDetail}>Tipo</th>
                                        <th style={thDetail}>Concepto</th>
                                        <th style={thDetail}>Cant./horas</th>
                                        <th style={thDetail}>Valor</th>
                                        <th style={thDetail}>Importe</th>
                                        <th style={thDetail}>Motivo</th>
                                        <th style={thDetail}>Observación(es)</th>
                                        <th style={thDetail}>Servicio</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {(row.detalle || []).map((d) => (
                                        <tr key={`${d.kind}-${d.id}`}>
                                          <td style={tdDetail}>{formatDate(d.fecha_realizacion)}</td>
                                          <td style={tdDetail}>{d.tipo}</td>
                                          <td style={tdDetail}>{d.concepto}</td>
                                          <td style={tdDetail}>
                                            {d.cantidad_horas != null ? formatNumber(d.cantidad_horas) : "—"}
                                          </td>
                                          <td style={tdDetail}>
                                            {d.valor_unitario != null ? formatMoney(d.valor_unitario) : "—"}
                                          </td>
                                          <td style={tdDetail}>{formatMoney(d.importe)}</td>
                                          <td style={tdDetail}>{d.motivo_label || "—"}</td>
                                          <td style={tdDetail}>
                                            {(d.observaciones || []).length
                                              ? (d.observaciones || []).join(" · ")
                                              : "—"}
                                          </td>
                                          <td style={tdDetail}>{d.servicio_nombre}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              </td>
                            </tr>
                          ) : null}
                        </Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}
