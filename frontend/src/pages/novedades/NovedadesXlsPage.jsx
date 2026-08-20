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

function formatDateOnly(value) {
  if (!value) return "—";
  const d = typeof value === "string" && value.length <= 10 ? new Date(`${value}T12:00:00`) : new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleDateString("es-AR");
}

function formatDateTime(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString("es-AR");
}

function tipoLabel(tipo) {
  if (tipo === "modulo_asignado") return "Módulo";
  if (!tipo) return "—";
  return "Novedad";
}

function bonoOptionLabels(bonoColumns) {
  const map = new Map();
  for (const col of bonoColumns || []) {
    const key = col.opcion_key || col.key;
    if (!map.has(key)) {
      map.set(key, col.label?.replace(/\s*·\s*subtotal$/i, "") || key);
    }
  }
  return map;
}

export function NovedadesXlsPage() {
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [rows, setRows] = useState([]);
  const [bonoColumns, setBonoColumns] = useState([]);
  const [opcionesSinTarifa, setOpcionesSinTarifa] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [periodoId, setPeriodoId] = useState("");
  const [bootstrapped, setBootstrapped] = useState(false);
  const [filterText, setFilterText] = useState("");
  const [sortKey, setSortKey] = useState("professional_name");
  const [sortDir, setSortDir] = useState("asc");

  const [modalRow, setModalRow] = useState(null);
  const [importe, setImporte] = useState("");
  const [comentario, setComentario] = useState("");
  const [saving, setSaving] = useState(false);

  const [detailRow, setDetailRow] = useState(null);
  const [detailItems, setDetailItems] = useState([]);
  const [detailAjustes, setDetailAjustes] = useState([]);
  const [detailLoading, setDetailLoading] = useState(false);

  const [updating, setUpdating] = useState(false);
  const [soloOpen, setSoloOpen] = useState(false);
  const [soloRows, setSoloRows] = useState([]);
  const [soloLoading, setSoloLoading] = useState(false);

  const selectedPeriodo = useMemo(
    () => periodos.find((p) => String(p.id) === String(periodoId)) || null,
    [periodos, periodoId]
  );
  const periodoClosed = selectedPeriodo?.estado === "closed";

  const optionLabels = useMemo(() => bonoOptionLabels(bonoColumns), [bonoColumns]);

  const loadGrid = async (pid = periodoId) => {
    setError("");
    try {
      const params = new URLSearchParams();
      if (pid) params.set("periodo_id", pid);
      const qs = params.toString() ? `?${params}` : "";
      const grid = await apiRequestWithRefresh(`/novedades/capital-humano${qs}`);
      setRows(Array.isArray(grid?.rows) ? grid.rows : []);
      setBonoColumns(Array.isArray(grid?.columns) ? grid.columns : []);
      setOpcionesSinTarifa(Array.isArray(grid?.opciones_sin_tarifa) ? grid.opciones_sin_tarifa : []);
    } catch (err) {
      setError(err.message || "Error al cargar Capital Humano");
    }
  };

  const bootstrap = async () => {
    setError("");
    try {
      const p = await apiRequestWithRefresh("/novedades/periodos");
      const list = Array.isArray(p) ? p : [];
      setPeriodos(list);
      const open = list.find((x) => x.estado === "open");
      setPeriodoId(open ? String(open.id) : "");
    } catch (err) {
      setError(err.message || "Error al cargar períodos");
    } finally {
      setBootstrapped(true);
    }
  };

  const actualizar = async () => {
    if (!periodoId) {
      setError("Seleccioná un período antes de actualizar");
      return;
    }
    if (periodoClosed) {
      setError("El período está cerrado: no se puede reimportar bonos");
      return;
    }
    setUpdating(true);
    setError("");
    try {
      const summary = await apiRequestWithRefresh("/novedades/capital-humano/bonos/import", {
        method: "POST",
        body: JSON.stringify({ periodo_id: Number(periodoId) }),
      });
      setInfo(
        `Actualización OK. Recibidas: ${summary.received} · Matcheadas: ${summary.matched} · Solo bonos: ${summary.solo_bonos} · Columnas: ${summary.columns} · Ignorados: ${summary.ignored}`
      );
      await loadGrid(periodoId);
    } catch (err) {
      setError(err.message || "Error al actualizar bonos");
    } finally {
      setUpdating(false);
    }
  };

  const openSoloBonos = async () => {
    if (!periodoId) {
      setError("Seleccioná un período para ver solo bonos");
      return;
    }
    setSoloOpen(true);
    setSoloLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ periodo_id: periodoId });
      const list = await apiRequestWithRefresh(`/novedades/capital-humano/bonos/solo?${params}`);
      setSoloRows(list);
    } catch (err) {
      setError(err.message || "Error al cargar solo bonos");
      setSoloOpen(false);
    } finally {
      setSoloLoading(false);
    }
  };

  useEffect(() => {
    bootstrap();
  }, []);

  useEffect(() => {
    if (!bootstrapped) return;
    loadGrid(periodoId);
  }, [periodoId, bootstrapped]);

  const download = async (path, fallbackName) => {
    setError("");
    try {
      const params = new URLSearchParams();
      if (periodoId) params.set("periodo_id", periodoId);
      const qs = params.toString() ? `?${params}` : "";
      const { blob, filename } = await apiDownloadWithRefresh(`${path}${qs}`);
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

  const openAgregarAjuste = (row) => {
    if (!periodoId) {
      setError("Seleccioná un período para cargar ajustes");
      return;
    }
    setError("");
    setModalRow(row);
    setImporte("");
    setComentario("");
  };

  const closeModal = () => {
    if (saving) return;
    setModalRow(null);
  };

  const openDetalle = async (row) => {
    setError("");
    setDetailRow(row);
    setDetailItems([]);
    setDetailAjustes([]);
    setDetailLoading(true);
    try {
      const cargaParams = new URLSearchParams({
        professional_id: String(row.professional_id),
      });
      if (periodoId) cargaParams.set("periodo_id", periodoId);

      const requests = [apiRequestWithRefresh(`/novedades/grilla?${cargaParams}`)];
      if (periodoId) {
        const ajParams = new URLSearchParams({
          professional_id: String(row.professional_id),
          periodo_id: periodoId,
        });
        requests.push(apiRequestWithRefresh(`/novedades/capital-humano/ajustes?${ajParams}`));
      }

      const [cargas, ajustesList] = await Promise.all(requests);
      setDetailItems(Array.isArray(cargas) ? cargas : []);
      setDetailAjustes(Array.isArray(ajustesList) ? ajustesList : []);
    } catch (err) {
      setError(err.message || "Error al cargar el detalle");
      setDetailRow(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetalle = () => {
    setDetailRow(null);
    setDetailItems([]);
    setDetailAjustes([]);
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
          servicio_id: null,
          importe: amount,
          comentario: comentario.trim(),
        }),
      });
      setInfo("Ajuste registrado");
      setImporte("");
      setComentario("");
      setModalRow(null);
      await loadGrid(periodoId);
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

  const detailProduccionRows = useMemo(() => {
    if (!detailRow) return [];
    const bonos = detailRow.bonos || {};
    const subtotales = detailRow.bonos_subtotales || {};
    const keys = new Set([...Object.keys(bonos), ...Object.keys(subtotales)]);
    return [...keys]
      .sort((a, b) => compareText(optionLabels.get(a) || a, optionLabels.get(b) || b))
      .map((key) => ({
        key,
        label: optionLabels.get(key) || key,
        cantidad: bonos[key] ?? 0,
        subtotal: subtotales[key] ?? 0,
      }));
  }, [detailRow, optionLabels]);

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Capital Humano</h1>
      <p style={uiStyles.helpText}>
        Seleccioná el período (por defecto el abierto) y pulsá <strong>Actualizar</strong> para importar bonos del
        período. La grilla muestra totales por profesional: cargas de jefes, ajustes, producción (bonos valorizados) y
        total general. En <strong>Detalle</strong> ves el desglose. Con período cerrado no se puede actualizar.
        Profesionales solo-bonos especiales (DEA/DEP/CAP/CAI) entran a la grilla; el resto en Solo bonos. Tarifas en
        Parametrización → Producción. Los Excel se rediseñarán en un change posterior.
      </p>
      {opcionesSinTarifa.length ? (
        <p
          style={{
            ...uiStyles.helpText,
            padding: "10px 12px",
            background: "#fff8e6",
            border: `1px solid ${uiTheme.colors.border}`,
            borderRadius: uiTheme.radius.sm,
            marginBottom: 12,
          }}
        >
          Hay opciones de bonos sin tarifa en Producción. Total producción cuenta esos subtotales en 0 hasta que
          cargues el valor unitario ({opcionesSinTarifa.length} opción
          {opcionesSinTarifa.length === 1 ? "" : "es"}).
        </p>
      ) : null}
      <AlertModal open={Boolean(error)} title="Atención" message={error} onClose={() => setError("")} />
      <AlertModal open={Boolean(info)} title="Listo" message={info} onClose={() => setInfo("")} />

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12, alignItems: "center" }}>
        <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)} style={uiStyles.formControl}>
          <option value="">Seleccioná período…</option>
          {periodos.map((p) => (
            <option key={p.id} value={p.id}>
              #{p.id} {p.nombre || ""} ({p.estado})
            </option>
          ))}
        </select>
        <button
          type="button"
          style={uiStyles.buttonPrimary}
          onClick={actualizar}
          disabled={updating || !periodoId || periodoClosed}
          title={
            !periodoId
              ? "Seleccioná un período"
              : periodoClosed
                ? "Período cerrado: bonos congelados"
                : "Importar bonos del período y refrescar"
          }
        >
          {updating ? "Actualizando…" : "Actualizar"}
        </button>
        <button type="button" style={uiStyles.buttonSecondary} onClick={openSoloBonos} disabled={!periodoId}>
          Solo bonos
        </button>
        <input
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          placeholder="Filtrar grilla (legajo / nombre)…"
          style={{ ...uiStyles.formControl, maxWidth: 280 }}
        />
        <button
          type="button"
          style={uiStyles.buttonSecondary}
          onClick={() => download("/novedades/export-capital.xlsx", "capital-humano.xlsx")}
        >
          Descargar XLS (agregado)
        </button>
        <button
          type="button"
          style={uiStyles.buttonSecondary}
          onClick={() => download("/novedades/export-capital-bonos.xlsx", "capital-humano-bonos.xlsx")}
        >
          XLS con bonos
        </button>
        <button
          type="button"
          style={uiStyles.buttonSecondary}
          onClick={() => download("/novedades/export.xlsx", "novedades-detalle.xlsx")}
        >
          Descargar XLS (detalle)
        </button>
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
                Total cargas{sortMark("monto_cargas")}
              </th>
              <th style={thStyle} onClick={() => toggleSort("monto_ajustes")}>
                Ajustes{sortMark("monto_ajustes")}
              </th>
              <th style={thStyle} onClick={() => toggleSort("monto_bonos")}>
                Total producción{sortMark("monto_bonos")}
              </th>
              <th style={thStyle} onClick={() => toggleSort("monto_total")}>
                Total general{sortMark("monto_total")}
              </th>
              <th style={{ ...thStyle, cursor: "default" }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row) => (
              <tr key={row.professional_id}>
                <td style={tdStyle}>{row.legajo || "—"}</td>
                <td style={tdStyle}>{row.professional_name}</td>
                <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>{formatMoney(row.monto_cargas)}</td>
                <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>{formatMoney(row.monto_ajustes)}</td>
                <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>
                  {formatMoney(row.monto_bonos ?? 0)}
                </td>
                <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>{formatMoney(row.monto_total)}</td>
                <td style={{ ...tdStyle, whiteSpace: "nowrap" }}>
                  <button
                    type="button"
                    style={{ ...uiStyles.buttonSecondary, marginRight: 6 }}
                    onClick={() => openDetalle(row)}
                  >
                    Detalle
                  </button>
                  <button type="button" style={uiStyles.buttonPrimary} onClick={() => openAgregarAjuste(row)}>
                    Agregar importe
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!visibleRows.length ? <p style={uiStyles.helpText}>Sin resultados.</p> : null}
      </div>

      {soloOpen ? (
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
          onClick={() => setSoloOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: uiTheme.radius.md,
              maxWidth: 860,
              width: "100%",
              padding: 22,
              boxShadow: uiTheme.shadow.md,
              border: `1px solid ${uiTheme.colors.border}`,
              marginBottom: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
              <div>
                <h2 style={{ marginTop: 0, marginBottom: 8, fontSize: "1.1rem" }}>Solo bonos</h2>
                <p style={{ ...uiStyles.helpText, marginTop: 0 }}>
                  Profesionales del catálogo con bonos en el período y sin cargas/ajustes (ni servicios especiales) en
                  la grilla.
                </p>
              </div>
              <button type="button" style={uiStyles.buttonSecondary} onClick={() => setSoloOpen(false)}>
                Cerrar
              </button>
            </div>
            {soloLoading ? (
              <p style={uiStyles.helpText}>Cargando…</p>
            ) : (
              <div style={{ overflowX: "auto", maxHeight: "60vh" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                  <thead>
                    <tr>
                      <th style={{ ...thStyle, cursor: "default" }}>CODPROF</th>
                      <th style={{ ...thStyle, cursor: "default" }}>Legajo</th>
                      <th style={{ ...thStyle, cursor: "default" }}>Profesional</th>
                      <th style={{ ...thStyle, cursor: "default" }}>Total cantidad</th>
                    </tr>
                  </thead>
                  <tbody>
                    {soloRows.map((row) => (
                      <tr key={row.professional_id}>
                        <td style={tdStyle}>{row.codprof}</td>
                        <td style={tdStyle}>{row.legajo || "—"}</td>
                        <td style={tdStyle}>{row.professional_name}</td>
                        <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>{row.total_cantidad}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!soloRows.length ? <p style={uiStyles.helpText}>No hay profesionales solo-bonos.</p> : null}
              </div>
            )}
          </div>
        </div>
      ) : null}

      {detailRow ? (
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
          onClick={closeDetalle}
        >
          <div
            role="dialog"
            aria-modal="true"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: uiTheme.radius.md,
              maxWidth: 960,
              width: "100%",
              padding: 22,
              boxShadow: uiTheme.shadow.md,
              border: `1px solid ${uiTheme.colors.border}`,
              marginBottom: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
              <div>
                <h2 style={{ marginTop: 0, marginBottom: 8, fontSize: "1.1rem" }}>
                  Detalle · {detailRow.professional_name}
                </h2>
                <p style={{ ...uiStyles.helpText, marginTop: 0 }}>
                  Legajo: {detailRow.legajo || "—"}
                  {periodoId ? ` · Período #${periodoId}` : ""}
                  {" · "}
                  Cargas {formatMoney(detailRow.monto_cargas)} · Producción {formatMoney(detailRow.monto_bonos ?? 0)} ·
                  Ajustes {formatMoney(detailRow.monto_ajustes)} · Total {formatMoney(detailRow.monto_total)}
                </p>
              </div>
              <button type="button" style={uiStyles.buttonSecondary} onClick={closeDetalle}>
                Cerrar
              </button>
            </div>

            {detailLoading ? (
              <p style={uiStyles.helpText}>Cargando…</p>
            ) : (
              <div style={{ display: "grid", gap: 20 }}>
                <section>
                  <h3 style={{ fontSize: "1rem", margin: "0 0 8px" }}>Cargas (módulos / novedades)</h3>
                  <div style={{ overflowX: "auto", maxHeight: "36vh" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem", minWidth: 720 }}>
                      <thead>
                        <tr>
                          <th style={{ ...thStyle, cursor: "default" }}>Tipo</th>
                          <th style={{ ...thStyle, cursor: "default" }}>Servicio</th>
                          <th style={{ ...thStyle, cursor: "default" }}>Concepto</th>
                          <th style={{ ...thStyle, cursor: "default" }}>Horas</th>
                          <th style={{ ...thStyle, cursor: "default" }}>Valor</th>
                          <th style={{ ...thStyle, cursor: "default" }}>F. realización</th>
                          <th style={{ ...thStyle, cursor: "default" }}>Período</th>
                          <th style={{ ...thStyle, cursor: "default" }}>F. carga</th>
                          <th style={{ ...thStyle, cursor: "default" }}>Cargado por</th>
                        </tr>
                      </thead>
                      <tbody>
                        {detailItems.map((item) => (
                          <tr key={`${item.tipo}-${item.id}`}>
                            <td style={tdStyle}>{tipoLabel(item.tipo)}</td>
                            <td style={tdStyle}>{item.servicio_nombre || "—"}</td>
                            <td style={tdStyle}>{item.concepto}</td>
                            <td style={tdStyle}>{item.horas != null ? item.horas : "—"}</td>
                            <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>
                              {formatMoney(item.valor)}
                            </td>
                            <td style={tdStyle}>{formatDateOnly(item.fecha_realizacion)}</td>
                            <td style={tdStyle}>{item.periodo_nombre || `#${item.periodo_id}`}</td>
                            <td style={{ ...tdStyle, whiteSpace: "nowrap", fontSize: 12 }}>
                              {formatDateTime(item.fecha_carga)}
                            </td>
                            <td style={tdStyle}>{item.cargado_por || "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {!detailItems.length ? (
                      <p style={uiStyles.helpText}>Sin cargas para este profesional en el período.</p>
                    ) : null}
                  </div>
                </section>

                <section>
                  <h3 style={{ fontSize: "1rem", margin: "0 0 8px" }}>Producción (bonos importados)</h3>
                  <div style={{ overflowX: "auto", maxHeight: "28vh" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                      <thead>
                        <tr>
                          <th style={{ ...thStyle, cursor: "default" }}>Opción</th>
                          <th style={{ ...thStyle, cursor: "default" }}>Cantidad</th>
                          <th style={{ ...thStyle, cursor: "default" }}>Subtotal</th>
                        </tr>
                      </thead>
                      <tbody>
                        {detailProduccionRows.map((r) => (
                          <tr key={r.key}>
                            <td style={tdStyle}>{r.label}</td>
                            <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>{r.cantidad}</td>
                            <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>
                              {formatMoney(r.subtotal)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {!detailProduccionRows.length ? (
                      <p style={uiStyles.helpText}>Sin bonos de producción para este profesional.</p>
                    ) : null}
                  </div>
                </section>

                <section>
                  <h3 style={{ fontSize: "1rem", margin: "0 0 8px" }}>Historial de ajustes</h3>
                  <ul style={{ ...uiStyles.listCard, maxHeight: 200, overflowY: "auto", margin: 0 }}>
                    {detailAjustes.map((a) => (
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
                          {a.created_by_name || "—"} ·{" "}
                          {a.created_at ? new Date(a.created_at).toLocaleString("es-AR") : ""}
                        </div>
                      </li>
                    ))}
                    {!detailAjustes.length ? (
                      <li style={{ padding: 10, color: uiTheme.colors.textMuted }}>Sin ajustes en este período.</li>
                    ) : null}
                  </ul>
                  <p style={{ ...uiStyles.helpText, marginTop: 8, marginBottom: 0 }}>
                    Para cargar un ajuste nuevo usá <strong>Agregar importe</strong> en la grilla.
                  </p>
                </section>
              </div>
            )}
          </div>
        </div>
      ) : null}

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
              maxWidth: 480,
              width: "100%",
              padding: 22,
              boxShadow: uiTheme.shadow.md,
              border: `1px solid ${uiTheme.colors.border}`,
              marginBottom: 24,
            }}
          >
            <h2 style={{ marginTop: 0, marginBottom: 8, fontSize: "1.1rem" }}>
              Agregar importe · {modalRow.professional_name}
            </h2>
            <p style={{ ...uiStyles.helpText, marginTop: 0 }}>
              Legajo: {modalRow.legajo || "—"} · Período #{periodoId}. El historial se ve en Detalle.
            </p>

            <form onSubmit={submitAjuste} style={{ display: "grid", gap: 10 }}>
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
                  Cancelar
                </button>
                <button type="submit" style={uiStyles.buttonPrimary} disabled={saving}>
                  {saving ? "Guardando…" : "Guardar ajuste"}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </section>
  );
}
