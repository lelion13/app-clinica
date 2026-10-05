import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { apiRequestWithRefresh, apiUploadWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

const PIE_COLORS = {
  Ocupado: "#0f766e",
  Libre: "#e2e8f0",
};
const PIE_LABEL_COLORS = {
  Ocupado: "#ffffff",
  Libre: "#334155",
};
const RADIAN = Math.PI / 180;

function todayISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function currentMonthISO() {
  return todayISO().slice(0, 7);
}

const filterField = {
  display: "flex",
  flexDirection: "column",
  gap: 2,
  fontSize: 11,
};

const filterSelect = {
  ...uiStyles.formControl,
  minWidth: 140,
  maxWidth: 220,
  fontSize: 13,
  padding: "6px 8px",
};

function formatHours(h) {
  if (h === null || h === undefined) return "—";
  const n = Number(h);
  return Number.isInteger(n) ? `${n}` : n.toFixed(2);
}

function formatPercent(p) {
  if (p === null || p === undefined) return "—";
  return `${p}%`;
}

/** Labels inside the donut slices; skip tiny slices to avoid clutter. */
function renderPieSliceLabel({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
  name,
  hoursLabel,
  percentLabel,
}) {
  if (!percent || percent < 0.07) return null;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.52;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  const fill = PIE_LABEL_COLORS[name] || uiTheme.colors.text;
  return (
    <text
      x={x}
      y={y}
      fill={fill}
      textAnchor="middle"
      dominantBaseline="central"
      style={{ fontSize: 12, fontWeight: 700, pointerEvents: "none" }}
    >
      <tspan x={x} dy="-0.55em">
        {percentLabel}%
      </tspan>
      <tspan x={x} dy="1.25em" style={{ fontSize: 11, fontWeight: 600 }}>
        {hoursLabel}h
      </tspan>
    </text>
  );
}

function TopTable({ title, items }) {
  return (
    <div
      style={{
        ...uiStyles.listCard,
        padding: 14,
        minWidth: 0,
        overflow: "auto",
      }}
    >
      <h3 style={{ margin: "0 0 10px", fontSize: 15 }}>{title}</h3>
      {!items?.length ? (
        <p style={{ margin: 0, fontSize: 13, color: uiTheme.colors.textMuted }}>Sin datos para el período.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ textAlign: "left", color: uiTheme.colors.textMuted }}>
              <th style={{ padding: "4px 6px 8px 0", fontWeight: 500 }}>Nombre</th>
              <th style={{ padding: "4px 6px 8px", fontWeight: 500 }}>Horas</th>
              <th style={{ padding: "4px 6px 8px", fontWeight: 500 }}>% box</th>
              <th style={{ padding: "4px 0 8px 6px", fontWeight: 500 }}>% ocup.</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.label} style={{ borderTop: `1px solid ${uiTheme.colors.border}` }}>
                <td style={{ padding: "8px 6px 8px 0", fontWeight: 600 }}>{row.label}</td>
                <td style={{ padding: "8px 6px" }}>{formatHours(row.hours)}</td>
                <td style={{ padding: "8px 6px" }}>{formatPercent(row.percent_box)}</td>
                <td style={{ padding: "8px 0 8px 6px" }}>{formatPercent(row.percent_occupied)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export function IndicadoresOcupacionPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState("day");
  const [day, setDay] = useState(() => todayISO());
  const [month, setMonth] = useState(() => currentMonthISO());
  const [locationId, setLocationId] = useState("");
  const [roomId, setRoomId] = useState("");
  const [especialidad, setEspecialidad] = useState("");
  const [medico, setMedico] = useState("");
  const [locations, setLocations] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [filterOptions, setFilterOptions] = useState({ especialidad: [], medico: [] });
  const [data, setData] = useState(null);
  const [turnosStats, setTurnosStats] = useState(null);
  const [importing, setImporting] = useState(false);
  const [unmatchedModal, setUnmatchedModal] = useState(null);
  const fileRef = useRef(null);

  useEffect(() => {
    safeLoad("/locations", setLocations, setError);
    safeLoad("/consulting-rooms", setRooms, setError);
    (async () => {
      try {
        const opts = await apiRequestWithRefresh("/distribucion/ocupacion/agenda/filter-options");
        setFilterOptions({
          especialidad: Array.isArray(opts?.especialidad) ? opts.especialidad : [],
          medico: Array.isArray(opts?.medico) ? opts.medico : [],
        });
      } catch (err) {
        setError(err.message || "No se pudieron cargar opciones de filtro");
      }
    })();
  }, []);

  const roomsForSelect = useMemo(() => {
    if (!locationId) return rooms;
    return rooms.filter((r) => String(r.location_id) === String(locationId));
  }, [rooms, locationId]);

  const filterParams = useCallback(() => {
    const params = new URLSearchParams({ period });
    if (period === "day") params.set("date", day);
    else params.set("month", month);
    if (locationId) params.set("location_id", locationId);
    if (roomId) params.set("room_id", roomId);
    if (especialidad) params.set("especialidad", especialidad);
    if (medico) params.set("medico", medico);
    return params;
  }, [period, day, month, locationId, roomId, especialidad, medico]);

  const load = useCallback(async () => {
    if (period === "day" && !day) return;
    if (period === "month" && !month) return;
    setLoading(true);
    setError("");
    try {
      const params = filterParams();
      const result = await apiRequestWithRefresh(`/distribucion/ocupacion/indicadores?${params}`);
      setData(result);
    } catch (err) {
      setData(null);
      setError(err.message || "No se pudieron calcular indicadores");
    } finally {
      setLoading(false);
    }
  }, [period, day, month, filterParams]);

  const loadTurnosStats = useCallback(async () => {
    if (period === "day" && !day) return;
    if (period === "month" && !month) return;
    try {
      const params = filterParams();
      const result = await apiRequestWithRefresh(`/distribucion/ocupacion/indicadores/turnos/stats?${params}`);
      setTurnosStats(result);
    } catch {
      setTurnosStats(null);
    }
  }, [period, day, month, filterParams]);

  useEffect(() => {
    load();
    loadTurnosStats();
  }, [load, loadTurnosStats]);

  useEffect(() => {
    if (roomId && !roomsForSelect.some((r) => String(r.id) === String(roomId))) {
      setRoomId("");
    }
  }, [roomsForSelect, roomId]);

  const onImportFile = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setImporting(true);
    setError("");
    setUnmatchedModal(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const result = await apiUploadWithRefresh("/distribucion/ocupacion/indicadores/turnos/import", form);
      setError("");
      await loadTurnosStats();
      if (result?.row_count != null) {
        setError(""); // clear
      }
    } catch (err) {
      if (err?.detail?.code === "unmatched_nombres") {
        setUnmatchedModal({
          message: err.detail.message || err.message,
          unmatched: Array.isArray(err.detail.unmatched) ? err.detail.unmatched : [],
          unmatched_count: err.detail.unmatched_count,
        });
      } else {
        setError(err.message || "No se pudo importar el CSV");
      }
    } finally {
      setImporting(false);
    }
  };

  const pieData = useMemo(() => {
    if (!data || !(data.enabled_hours > 0)) return [];
    const enabled = Number(data.enabled_hours) || 0;
    const occupied = Number(data.occupied_hours) || 0;
    const free = Number(data.free_hours) || 0;
    const pctOcc = enabled > 0 ? Math.round((occupied / enabled) * 1000) / 10 : 0;
    const pctFree = enabled > 0 ? Math.round((free / enabled) * 1000) / 10 : 0;
    return [
      {
        name: "Ocupado",
        value: occupied,
        hoursLabel: formatHours(occupied),
        percentLabel: pctOcc,
      },
      {
        name: "Libre",
        value: Math.max(0, free),
        hoursLabel: formatHours(Math.max(0, free)),
        percentLabel: pctFree,
      },
    ];
  }, [data]);

  const percentLabel =
    data?.occupancy_percent === null || data?.occupancy_percent === undefined
      ? "—"
      : `${data.occupancy_percent}%`;

  const periodHelp =
    period === "month"
      ? "% = horas sync mapeadas del mes ÷ horario operativo del box en todos los días del mes."
      : "% = horas de agendas sync mapeadas al consultorio ÷ horario operativo del box (ese día).";

  const withoutHoursLabel = period === "month" ? "Sin horario en el mes" : "Sin horario ese día";

  return (
    <section style={uiStyles.pageSection}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 10, marginBottom: 4 }}>
        <h1 style={{ ...uiStyles.sectionTitle, margin: 0, flex: "1 1 auto" }}>Indicadores ocupación</h1>
        <input
          ref={fileRef}
          type="file"
          accept=".csv,text/csv"
          style={{ display: "none" }}
          onChange={onImportFile}
        />
        <button
          type="button"
          style={uiStyles.buttonSecondary}
          disabled={importing}
          onClick={() => fileRef.current?.click()}
        >
          {importing ? "Importando…" : "Importar datos de turnos"}
        </button>
      </div>
      <p style={{ ...uiStyles.helpText, marginTop: 0 }}>
        {periodHelp} Especialidad/médico filtran solo horas ocupadas (payload). Puede superar 100% si el sync
        supera el horario del box.
        {loading ? " Calculando…" : ""}
      </p>

      {error ? <p style={{ color: uiTheme.colors.danger, marginBottom: 12 }}>{error}</p> : null}

      <div
        style={{
          display: "flex",
          flexWrap: "nowrap",
          gap: 8,
          alignItems: "flex-end",
          overflowX: "auto",
          marginBottom: 16,
          paddingBottom: 2,
        }}
      >
        <label style={filterField}>
          Período
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            style={filterSelect}
          >
            <option value="day">Día</option>
            <option value="month">Mes</option>
          </select>
        </label>
        {period === "day" ? (
          <label style={filterField}>
            Día
            <input type="date" value={day} onChange={(e) => setDay(e.target.value)} style={filterSelect} />
          </label>
        ) : (
          <label style={filterField}>
            Mes
            <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} style={filterSelect} />
          </label>
        )}
        <label style={filterField}>
          Ubicación
          <select
            value={locationId}
            onChange={(e) => setLocationId(e.target.value)}
            style={filterSelect}
          >
            <option value="">Todas</option>
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name}
                {loc.tipo ? ` · ${loc.tipo}` : ""}
              </option>
            ))}
          </select>
        </label>
        <label style={filterField}>
          Consultorio
          <select value={roomId} onChange={(e) => setRoomId(e.target.value)} style={filterSelect}>
            <option value="">Todos</option>
            {roomsForSelect.map((r) => (
              <option key={r.id} value={r.id}>
                {r.code}
              </option>
            ))}
          </select>
        </label>
        <label style={filterField}>
          Especialidad
          <select
            value={especialidad}
            onChange={(e) => setEspecialidad(e.target.value)}
            style={filterSelect}
          >
            <option value="">Todas</option>
            {filterOptions.especialidad.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label || opt.value}
              </option>
            ))}
          </select>
        </label>
        <label style={filterField}>
          Médico
          <select value={medico} onChange={(e) => setMedico(e.target.value)} style={filterSelect}>
            <option value="">Todos</option>
            {filterOptions.medico.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label || opt.value}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: 12,
          marginBottom: 20,
        }}
      >
        <div style={{ ...uiStyles.listCard, padding: 14 }}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Ocupación</div>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{percentLabel}</div>
        </div>
        <div style={{ ...uiStyles.listCard, padding: 14 }}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Horas ocupadas (sync)</div>
          <div style={{ fontSize: 22, fontWeight: 700 }}>{data ? formatHours(data.occupied_hours) : "—"}</div>
        </div>
        <div style={{ ...uiStyles.listCard, padding: 14 }}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Horas habilitadas</div>
          <div style={{ fontSize: 22, fontWeight: 700 }}>{data ? formatHours(data.enabled_hours) : "—"}</div>
        </div>
        <div style={{ ...uiStyles.listCard, padding: 14 }}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Consultorios en torta</div>
          <div style={{ fontSize: 22, fontWeight: 700 }}>{data ? data.rooms_in_pie : "—"}</div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: 16,
          marginBottom: 16,
          alignItems: "stretch",
        }}
      >
        <div
          style={{
            ...uiStyles.listCard,
            padding: 14,
            minWidth: 0,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <h3 style={{ margin: "0 0 4px", fontSize: 15 }}>Ocupación del box</h3>
          <p style={{ margin: "0 0 8px", fontSize: 12, color: uiTheme.colors.textMuted }}>
            Horas sync mapeadas vs horario habilitado
          </p>
          {pieData.length ? (
            <>
              <div style={{ position: "relative", width: "100%", height: 260, flex: 1 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={68}
                      outerRadius={108}
                      paddingAngle={3}
                      stroke={uiTheme.colors.surface}
                      strokeWidth={3}
                      labelLine={false}
                      label={renderPieSliceLabel}
                      isAnimationActive={!loading}
                    >
                      {pieData.map((entry) => (
                        <Cell key={entry.name} fill={PIE_COLORS[entry.name] || "#94a3b8"} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value, name, item) => {
                        const pct = item?.payload?.percentLabel;
                        return [`${formatHours(value)} h (${pct}%)`, name];
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div
                  style={{
                    position: "absolute",
                    inset: 0,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    pointerEvents: "none",
                  }}
                >
                  <div
                    style={{
                      fontSize: 28,
                      fontWeight: 800,
                      letterSpacing: "-0.02em",
                      color: uiTheme.colors.text,
                      lineHeight: 1,
                    }}
                  >
                    {percentLabel}
                  </div>
                  <div
                    style={{
                      marginTop: 4,
                      fontSize: 11,
                      fontWeight: 600,
                      color: uiTheme.colors.textMuted,
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                    }}
                  >
                    ocupación
                  </div>
                </div>
              </div>
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 10,
                  justifyContent: "center",
                  marginTop: 4,
                }}
              >
                {pieData.map((entry) => (
                  <div
                    key={entry.name}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: "6px 10px",
                      borderRadius: uiTheme.radius.sm,
                      background: uiTheme.colors.surfaceMuted,
                      border: `1px solid ${uiTheme.colors.border}`,
                      fontSize: 12,
                    }}
                  >
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: 3,
                        background: PIE_COLORS[entry.name],
                        flexShrink: 0,
                      }}
                    />
                    <span style={{ fontWeight: 600, color: uiTheme.colors.text }}>{entry.name}</span>
                    <span style={{ color: uiTheme.colors.textMuted }}>
                      {entry.hoursLabel}h · {entry.percentLabel}%
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p style={{ color: uiTheme.colors.textMuted, fontSize: 13, margin: "auto 0" }}>
              {loading
                ? "Calculando…"
                : "Sin horas habilitadas para la torta (consultorios sin horario en el período, o sin consultorios)."}
            </p>
          )}
        </div>
        <TopTable title="Top especialidad" items={data?.top_especialidad} />
        <TopTable title="Top médico" items={data?.top_medico} />
      </div>

      <div
        style={{
          ...uiStyles.listCard,
          padding: 14,
          marginBottom: 16,
        }}
      >
        <h3 style={{ margin: "0 0 4px", fontSize: 15 }}>Turnos importados</h3>
        <p style={{ margin: "0 0 12px", fontSize: 12, color: uiTheme.colors.textMuted }}>
          Match por nombre de agenda (sync). KPIs según período y filtros de arriba. Universo: AT+AU.
        </p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
            gap: 12,
          }}
        >
          <div>
            <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Cantidad de turnos</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{turnosStats ? turnosStats.turnos : "—"}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Turnos ausentes</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{turnosStats ? turnosStats.ausentes : "—"}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Ausentismo</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>
              {turnosStats ? formatPercent(turnosStats.ausentismo_percent) : "—"}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Prom. presente→atendido</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>
              {turnosStats?.avg_presente_atendido_minutes != null
                ? `${turnosStats.avg_presente_atendido_minutes} min`
                : "—"}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Prom. espera (reserva→turno)</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>
              {turnosStats?.avg_espera_dias != null ? `${turnosStats.avg_espera_dias} días` : "—"}
            </div>
          </div>
        </div>
        {turnosStats?.imports?.length ? (
          <p style={{ margin: "12px 0 0", fontSize: 12, color: uiTheme.colors.textMuted }}>
            Imports:{" "}
            {turnosStats.imports
              .slice(0, 5)
              .map((i) => `${i.filename} (${i.period_start}→${i.period_end}, ${i.rows} filas)`)
              .join(" · ")}
          </p>
        ) : (
          <p style={{ margin: "12px 0 0", fontSize: 12, color: uiTheme.colors.textMuted }}>
            Todavía no hay CSV importados.
          </p>
        )}
      </div>

      {data?.rooms_without_hours?.length ? (
        <div
          style={{
            marginBottom: 12,
            padding: "10px 12px",
            borderRadius: uiTheme.radius.md,
            border: `1px solid ${uiTheme.colors.borderStrong}`,
            background: uiTheme.colors.surfaceMuted,
            fontSize: 13,
          }}
        >
          <strong>
            {withoutHoursLabel} ({data.rooms_without_hours.length}):
          </strong>{" "}
          {data.rooms_without_hours.map((r) => r.code).join(", ")}
          <div style={{ fontSize: 12, marginTop: 4, color: uiTheme.colors.textMuted }}>
            No entran en el denominador ni en la torta. Configurá franjas en Consultorios → Horarios.
          </div>
        </div>
      ) : null}

      {data?.rooms_without_agenda ? (
        <p style={{ fontSize: 13, color: uiTheme.colors.textMuted }}>
          Consultorios con horario pero sin agenda mapeada: {data.rooms_without_agenda} (aportan 0% al numerador).
        </p>
      ) : null}

      {unmatchedModal ? (
        <div
          role="presentation"
          onClick={() => setUnmatchedModal(null)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 60,
            background: "rgba(15, 23, 42, 0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "min(520px, 100%)",
              maxHeight: "min(80vh, 560px)",
              overflowY: "auto",
              background: uiTheme.colors.surface,
              border: `1px solid ${uiTheme.colors.borderStrong}`,
              borderRadius: uiTheme.radius.md,
              boxShadow: "0 16px 40px rgba(0,0,0,0.22)",
              padding: 16,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 10 }}>
              <strong style={{ fontSize: 14 }}>Import rechazado — sin match de agenda</strong>
              <button
                type="button"
                style={{ ...uiStyles.buttonSecondary, padding: "2px 10px" }}
                onClick={() => setUnmatchedModal(null)}
              >
                Cerrar
              </button>
            </div>
            <p style={{ margin: "0 0 10px", fontSize: 13 }}>{unmatchedModal.message}</p>
            <p style={{ margin: "0 0 8px", fontSize: 12, color: uiTheme.colors.textMuted }}>
              Mostrando {unmatchedModal.unmatched.length}
              {unmatchedModal.unmatched_count > unmatchedModal.unmatched.length
                ? ` de ${unmatchedModal.unmatched_count}`
                : ""}{" "}
              fila(s). El Nombre del CSV debe coincidir con nombre_agenda del sync (normalizado).
            </p>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, lineHeight: 1.45 }}>
              {unmatchedModal.unmatched.map((u) => (
                <li key={`${u.row}-${u.nombre}`}>
                  Fila {u.row}: {u.nombre}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
    </section>
  );
}
