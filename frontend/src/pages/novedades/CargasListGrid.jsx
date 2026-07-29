import { useMemo, useState } from "react";

import { uiStyles, uiTheme } from "../../ui/theme";

const thStyle = {
  textAlign: "left",
  padding: "10px 12px",
  borderBottom: `1px solid ${uiTheme.colors.borderStrong}`,
  background: uiTheme.colors.surfaceMuted,
  color: uiTheme.colors.textMuted,
  fontSize: 12,
  fontWeight: 600,
  letterSpacing: 0.02,
  whiteSpace: "nowrap",
  cursor: "pointer",
  userSelect: "none",
};

const tdStyle = {
  padding: "10px 12px",
  borderBottom: `1px solid ${uiTheme.colors.border}`,
  color: uiTheme.colors.text,
  verticalAlign: "middle",
};

const badgeBase = {
  display: "inline-block",
  padding: "2px 8px",
  borderRadius: uiTheme.radius.sm,
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: 0.02,
};

function formatMoney(value) {
  if (value == null || value === "") return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  return `$${n.toLocaleString("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString("es-AR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
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

/**
 * Unified sortable/filterable grid for módulo assignments + novedades.
 */
export function CargasListGrid({ rows, onAnular }) {
  const [filterText, setFilterText] = useState("");
  const [filterTipo, setFilterTipo] = useState("");
  const [filterServicio, setFilterServicio] = useState("");
  const [sortKey, setSortKey] = useState("servicio");
  const [sortDir, setSortDir] = useState("asc");

  const serviciosOptions = useMemo(() => {
    const map = new Map();
    rows.forEach((row) => {
      if (row.servicio_id != null) {
        map.set(String(row.servicio_id), row.servicio_nombre || `Servicio #${row.servicio_id}`);
      }
    });
    return [...map.entries()]
      .map(([id, nombre]) => ({ id, nombre }))
      .sort((a, b) => compareText(a.nombre, b.nombre));
  }, [rows]);

  const visibleRows = useMemo(() => {
    const q = filterText.trim().toLowerCase();
    let filtered = rows.filter((row) => {
      if (filterTipo && row.kind !== filterTipo) return false;
      if (filterServicio && String(row.servicio_id) !== String(filterServicio)) return false;
      if (!q) return true;
      const haystack = [
        row.servicio_nombre,
        row.professional_name,
        row.concepto,
        row.periodo_nombre,
        row.kind_label,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    });

    const dir = sortDir === "asc" ? 1 : -1;
    filtered = [...filtered].sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case "profesional":
          cmp = compareText(a.professional_name, b.professional_name);
          if (cmp === 0) cmp = compareText(a.servicio_nombre, b.servicio_nombre);
          break;
        case "concepto":
          cmp = compareText(a.concepto, b.concepto);
          break;
        case "tipo":
          cmp = compareText(a.kind_label, b.kind_label);
          break;
        case "horas":
          cmp = compareNumber(a.horas, b.horas);
          break;
        case "valor":
          cmp = compareNumber(a.valor, b.valor);
          break;
        case "fecha":
          cmp = compareText(a.fecha_carga, b.fecha_carga);
          break;
        case "periodo":
          cmp = compareText(a.periodo_nombre || a.periodo_id, b.periodo_nombre || b.periodo_id);
          break;
        case "servicio":
        default:
          cmp = compareText(a.servicio_nombre, b.servicio_nombre);
          if (cmp === 0) cmp = compareText(a.professional_name, b.professional_name);
          break;
      }
      if (cmp === 0) cmp = compareNumber(b.id, a.id);
      return cmp * dir;
    });

    return filtered;
  }, [rows, filterText, filterTipo, filterServicio, sortKey, sortDir]);

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(key);
    setSortDir("asc");
  };

  const sortMark = (key) => {
    if (sortKey !== key) return "";
    return sortDir === "asc" ? " ↑" : " ↓";
  };

  const anular = async (row) => {
    if (!onAnular) return;
    await onAnular(row);
  };

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <input
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          placeholder="Filtrar por servicio, profesional, concepto…"
          style={{ ...uiStyles.formControl, minWidth: 220, flex: "1 1 220px" }}
        />
        <select
          value={filterTipo}
          onChange={(e) => setFilterTipo(e.target.value)}
          style={uiStyles.formControl}
        >
          <option value="">Todos los tipos</option>
          <option value="modulo">Módulo</option>
          <option value="novedad">Novedad</option>
        </select>
        <select
          value={filterServicio}
          onChange={(e) => setFilterServicio(e.target.value)}
          style={uiStyles.formControl}
        >
          <option value="">Todos los servicios</option>
          {serviciosOptions.map((s) => (
            <option key={s.id} value={s.id}>{s.nombre}</option>
          ))}
        </select>
        <span style={uiStyles.helpText}>
          {visibleRows.length} de {rows.length}
        </span>
      </div>

      <div
        style={{
          overflowX: "auto",
          border: `1px solid ${uiTheme.colors.border}`,
          borderRadius: uiTheme.radius.md,
          background: uiTheme.colors.surface,
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem", minWidth: 720 }}>
          <thead>
            <tr>
              <th style={thStyle} onClick={() => toggleSort("tipo")}>Tipo{sortMark("tipo")}</th>
              <th style={thStyle} onClick={() => toggleSort("servicio")}>Servicio{sortMark("servicio")}</th>
              <th style={thStyle} onClick={() => toggleSort("profesional")}>Profesional{sortMark("profesional")}</th>
              <th style={thStyle} onClick={() => toggleSort("concepto")}>Concepto{sortMark("concepto")}</th>
              <th style={thStyle} onClick={() => toggleSort("horas")}>Horas{sortMark("horas")}</th>
              <th style={thStyle} onClick={() => toggleSort("valor")}>Valor{sortMark("valor")}</th>
              <th style={thStyle} onClick={() => toggleSort("periodo")}>Período{sortMark("periodo")}</th>
              <th style={thStyle} onClick={() => toggleSort("fecha")}>Fecha{sortMark("fecha")}</th>
              <th style={{ ...thStyle, cursor: "default" }}> </th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row) => (
              <tr key={`${row.kind}-${row.id}`}>
                <td style={tdStyle}>
                  <span
                    style={{
                      ...badgeBase,
                      background: row.kind === "modulo" ? uiTheme.colors.primarySoft : "#f0f7f5",
                      color: row.kind === "modulo" ? uiTheme.colors.primaryStrong : "#3d5c56",
                      border: `1px solid ${row.kind === "modulo" ? uiTheme.colors.border : uiTheme.colors.borderStrong}`,
                    }}
                  >
                    {row.kind_label}
                  </span>
                </td>
                <td style={tdStyle}>{row.servicio_nombre || "—"}</td>
                <td style={{ ...tdStyle, fontWeight: 500 }}>{row.professional_name || "—"}</td>
                <td style={tdStyle}>{row.concepto}</td>
                <td style={tdStyle}>{row.horas != null ? row.horas : "—"}</td>
                <td style={{ ...tdStyle, fontVariantNumeric: "tabular-nums" }}>{formatMoney(row.valor)}</td>
                <td style={tdStyle}>{row.periodo_nombre || `#${row.periodo_id}`}</td>
                <td style={{ ...tdStyle, whiteSpace: "nowrap", color: uiTheme.colors.textMuted, fontSize: 13 }}>
                  {formatDate(row.fecha_carga)}
                </td>
                <td style={tdStyle}>
                  <button type="button" style={uiStyles.buttonDanger} onClick={() => anular(row)}>
                    anular
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!visibleRows.length ? (
          <p style={{ ...uiStyles.helpText, margin: 0, padding: 16 }}>
            {rows.length ? "Sin resultados para el filtro." : "Todavía no hay cargas en tu alcance."}
          </p>
        ) : null}
      </div>
    </div>
  );
}
