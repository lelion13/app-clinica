import { useEffect, useMemo, useRef, useState } from "react";

import {
  applyColumnFilters,
  buildIndicators,
  distinctColumnValues,
  filterValueLabel,
  formatMetric,
} from "../lib/ocupacionIndicators";
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
  verticalAlign: "top",
};

const tdStyle = {
  padding: "8px 10px",
  borderBottom: `1px solid ${uiTheme.colors.border}`,
  color: uiTheme.colors.text,
  verticalAlign: "top",
};

function emptyFilters() {
  return Object.fromEntries(COLUMNS.map((col) => [col.key, []]));
}

function ColumnMultiFilter({ options, selected, onChange }) {
  const rootRef = useRef(null);
  const [open, setOpen] = useState(false);
  const count = selected.length;
  const summary = count === 0 ? "Todos" : `${count} sel.`;

  useEffect(() => {
    if (!open) return undefined;
    const onPointerDown = (event) => {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  const toggle = (token) => {
    if (selected.includes(token)) {
      onChange(selected.filter((value) => value !== token));
    } else {
      onChange([...selected, token]);
    }
  };

  return (
    <div ref={rootRef} style={{ position: "relative", marginTop: 6, minWidth: 110 }}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        style={{
          ...uiStyles.buttonSecondary,
          width: "100%",
          padding: "4px 8px",
          fontSize: 11,
          fontWeight: count ? 600 : 500,
          textAlign: "left",
        }}
      >
        {summary}
      </button>
      {open ? (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 4px)",
            left: 0,
            zIndex: 30,
            minWidth: 180,
            maxHeight: 220,
            overflowY: "auto",
            background: uiTheme.colors.surface,
            border: `1px solid ${uiTheme.colors.border}`,
            borderRadius: uiTheme.radius.sm,
            boxShadow: uiTheme.shadow.md,
            padding: 8,
          }}
        >
          <button
            type="button"
            onClick={() => onChange([])}
            style={{
              ...uiStyles.buttonSecondary,
              width: "100%",
              marginBottom: 6,
              padding: "4px 8px",
              fontSize: 11,
            }}
          >
            Limpiar
          </button>
          {options.map((token) => (
            <label
              key={token}
              style={{
                display: "flex",
                gap: 6,
                alignItems: "flex-start",
                fontSize: 12,
                fontWeight: 400,
                color: uiTheme.colors.text,
                padding: "3px 2px",
                cursor: "pointer",
              }}
            >
              <input
                type="checkbox"
                checked={selected.includes(token)}
                onChange={() => toggle(token)}
                style={{ marginTop: 2 }}
              />
              <span style={{ wordBreak: "break-word" }}>{filterValueLabel(token)}</span>
            </label>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function IndicatorsModal({ open, rows, filteredCount, onClose }) {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (event) => {
      if (event.key === "Escape") onClose?.();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
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
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="ocupacion-indicators-title"
        onClick={(event) => event.stopPropagation()}
        style={{
          background: "#fff",
          borderRadius: uiTheme.radius.md,
          maxWidth: 920,
          width: "100%",
          marginBottom: 24,
          padding: 22,
          boxShadow: uiTheme.shadow.md,
          border: `1px solid ${uiTheme.colors.border}`,
        }}
      >
        <h2
          id="ocupacion-indicators-title"
          style={{ marginTop: 0, marginBottom: 8, fontSize: "1.1rem", color: uiTheme.colors.text }}
        >
          Indicadores (filtro actual)
        </h2>
        <p style={{ ...uiStyles.helpText, marginTop: 0, marginBottom: 14 }}>
          Agrupado por id_dominio + especialidad + medico + dia (sin filas sin dia). Horas = diferencia de
          horario; turnos/sobreturnos sumados desde la API. Filas en grilla: {filteredCount}. Grupos:{" "}
          {rows.length}.
        </p>
        <div
          style={{
            overflowX: "auto",
            border: `1px solid ${uiTheme.colors.border}`,
            borderRadius: uiTheme.radius.md,
            marginBottom: 16,
          }}
        >
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem", minWidth: 720 }}>
            <thead>
              <tr>
                {[
                  "id_dominio",
                  "especialidad",
                  "medico",
                  "dia",
                  "horas",
                  "cantidad_turnos",
                  "cantidad_sobreturno",
                ].map((label) => (
                  <th key={label} style={thStyle}>
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ ...tdStyle, color: uiTheme.colors.textMuted }}>
                    No hay filas válidas para calcular indicadores con el filtro actual.
                  </td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr key={`${row.id_dominio}|${row.especialidad}|${row.medico}|${row.dia}`}>
                    <td style={tdStyle}>{row.id_dominio}</td>
                    <td style={tdStyle}>{row.especialidad}</td>
                    <td style={tdStyle}>{row.medico}</td>
                    <td style={tdStyle}>{row.dia}</td>
                    <td style={tdStyle}>{formatMetric(row.horas)}</td>
                    <td style={tdStyle}>{formatMetric(row.cantidad_turnos)}</td>
                    <td style={tdStyle}>{formatMetric(row.cantidad_sobreturno)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button type="button" onClick={onClose} style={uiStyles.buttonPrimary}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}

export function OccupancyPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [items, setItems] = useState([]);
  const [filters, setFilters] = useState(emptyFilters);
  const [indicatorsOpen, setIndicatorsOpen] = useState(false);
  const [syncInfo, setSyncInfo] = useState("");

  const loadFromDb = async ({ resetFilters = false } = {}) => {
    setError("");
    setLoading(true);
    try {
      const data = await apiRequestWithRefresh("/distribucion/ocupacion/horarios-activos");
      setItems(Array.isArray(data?.items) ? data.items : []);
      if (resetFilters) setFilters(emptyFilters());
    } catch (err) {
      setItems([]);
      setError(err.message || "No se pudieron cargar los horarios activos");
    } finally {
      setLoading(false);
    }
  };

  const syncAndReload = async () => {
    setError("");
    setSyncInfo("");
    setSyncing(true);
    try {
      const result = await apiRequestWithRefresh("/distribucion/ocupacion/horarios-activos/sync", {
        method: "POST",
      });
      const synced = Number(result?.synced) || 0;
      const skipped = Number(result?.skipped) || 0;
      setSyncInfo(`Sincronizado: ${synced} filas${skipped ? ` (${skipped} omitidas)` : ""}.`);
      await loadFromDb({ resetFilters: true });
    } catch (err) {
      setError(err.message || "No se pudo sincronizar contra la API externa");
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    loadFromDb();
  }, []);

  const filterOptions = useMemo(() => {
    const map = {};
    for (const col of COLUMNS) {
      map[col.key] = distinctColumnValues(items, col.key);
    }
    return map;
  }, [items]);

  const filteredItems = useMemo(() => applyColumnFilters(items, filters), [items, filters]);

  const indicatorRows = useMemo(
    () => (indicatorsOpen ? buildIndicators(filteredItems) : []),
    [indicatorsOpen, filteredItems]
  );

  const activeFilterCount = COLUMNS.reduce((acc, col) => acc + (filters[col.key]?.length ? 1 : 0), 0);

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
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          <button
            type="button"
            onClick={() => setFilters(emptyFilters())}
            disabled={loading || syncing || activeFilterCount === 0}
            style={uiStyles.buttonSecondary}
          >
            Limpiar filtros
          </button>
          <button
            type="button"
            onClick={() => setIndicatorsOpen(true)}
            disabled={loading || syncing || filteredItems.length === 0}
            style={uiStyles.buttonPrimary}
          >
            Indicadores
          </button>
          <button
            type="button"
            onClick={syncAndReload}
            disabled={loading || syncing}
            style={uiStyles.buttonSecondary}
          >
            {syncing ? "Sincronizando..." : "Actualizar"}
          </button>
        </div>
      </div>
      <p style={uiStyles.helpText}>
        Datos locales (DB). Actualizar sincroniza desde la API externa (reemplazo total) y recarga.
        Filtrá por columna e Indicadores sobre el resultado.
        {loading || syncing ? "" : ` Mostrando ${filteredItems.length} de ${items.length}.`}
      </p>
      {syncInfo ? <p style={{ color: uiTheme.colors.primaryStrong, marginTop: 0 }}>{syncInfo}</p> : null}
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
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem", minWidth: 960 }}>
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th key={col.key} style={thStyle}>
                  <div>{col.label}</div>
                  <ColumnMultiFilter
                    options={filterOptions[col.key] || []}
                    selected={filters[col.key] || []}
                    onChange={(next) => setFilters((prev) => ({ ...prev, [col.key]: next }))}
                  />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredItems.map((row, index) => (
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

      <IndicatorsModal
        open={indicatorsOpen}
        rows={indicatorRows}
        filteredCount={filteredItems.length}
        onClose={() => setIndicatorsOpen(false)}
      />
    </section>
  );
}
