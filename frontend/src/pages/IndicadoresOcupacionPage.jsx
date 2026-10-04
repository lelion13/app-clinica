import { useCallback, useEffect, useMemo, useState } from "react";
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

const PIE_COLORS = ["#0f766e", "#cbd5e1"];

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

  const load = useCallback(async () => {
    if (period === "day" && !day) return;
    if (period === "month" && !month) return;
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ period });
      if (period === "day") params.set("date", day);
      else params.set("month", month);
      if (locationId) params.set("location_id", locationId);
      if (roomId) params.set("room_id", roomId);
      if (especialidad) params.set("especialidad", especialidad);
      if (medico) params.set("medico", medico);
      const result = await apiRequestWithRefresh(`/distribucion/ocupacion/indicadores?${params}`);
      setData(result);
    } catch (err) {
      setData(null);
      setError(err.message || "No se pudieron calcular indicadores");
    } finally {
      setLoading(false);
    }
  }, [period, day, month, locationId, roomId, especialidad, medico]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (roomId && !roomsForSelect.some((r) => String(r.id) === String(roomId))) {
      setRoomId("");
    }
  }, [roomsForSelect, roomId]);

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
      <h1 style={uiStyles.sectionTitle}>Indicadores ocupación</h1>
      <p style={{ ...uiStyles.helpText, marginTop: -6 }}>
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
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: 16,
          marginBottom: 16,
          alignItems: "stretch",
        }}
      >
        <div style={{ height: 320, minWidth: 0 }}>
          {pieData.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={110}
                  label={({ name, hoursLabel, percentLabel: pct }) => `${name}: ${hoursLabel}h (${pct}%)`}
                >
                  {pieData.map((_, index) => (
                    <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name, item) => {
                    const pct = item?.payload?.percentLabel;
                    return [`${formatHours(value)} h (${pct}%)`, name];
                  }}
                />
                <Legend
                  formatter={(value, entry) => {
                    const p = entry?.payload;
                    return `${value}: ${p?.hoursLabel ?? "—"}h (${p?.percentLabel ?? "—"}%)`;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: uiTheme.colors.textMuted, fontSize: 13 }}>
              {loading
                ? "Calculando…"
                : "Sin horas habilitadas para la torta (consultorios sin horario en el período, o sin consultorios)."}
            </p>
          )}
        </div>
        <TopTable title="Top especialidad" items={data?.top_especialidad} />
        <TopTable title="Top médico" items={data?.top_medico} />
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
    </section>
  );
}
