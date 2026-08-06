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

export function IndicadoresOcupacionPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [day, setDay] = useState(() => todayISO());
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
    if (!day) return;
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ date: day });
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
  }, [day, locationId, roomId, especialidad, medico]);

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
    return [
      { name: "Ocupado", value: data.occupied_hours },
      { name: "Libre", value: data.free_hours },
    ];
  }, [data]);

  const percentLabel =
    data?.occupancy_percent === null || data?.occupancy_percent === undefined
      ? "—"
      : `${data.occupancy_percent}%`;

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Indicadores ocupación</h1>
      <p style={{ ...uiStyles.helpText, marginTop: -6 }}>
        % = horas de agendas sync mapeadas al consultorio ÷ horario operativo del box (ese día). Especialidad/médico
        solo afectan las horas ocupadas. Puede superar 100% si el sync supera el horario del box.
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
          Día
          <input type="date" value={day} onChange={(e) => setDay(e.target.value)} style={filterSelect} />
        </label>
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
          <div style={{ fontSize: 22, fontWeight: 700 }}>{data ? data.occupied_hours : "—"}</div>
        </div>
        <div style={{ ...uiStyles.listCard, padding: 14 }}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Horas habilitadas</div>
          <div style={{ fontSize: 22, fontWeight: 700 }}>{data ? data.enabled_hours : "—"}</div>
        </div>
        <div style={{ ...uiStyles.listCard, padding: 14 }}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Consultorios en torta</div>
          <div style={{ fontSize: 22, fontWeight: 700 }}>{data ? data.rooms_in_pie : "—"}</div>
        </div>
      </div>

      <div style={{ height: 320, marginBottom: 16 }}>
        {pieData.length ? (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={110} label>
                {pieData.map((_, index) => (
                  <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => [`${v} h`, ""]} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p style={{ color: uiTheme.colors.textMuted, fontSize: 13 }}>
            {loading
              ? "Calculando…"
              : "Sin horas habilitadas para la torta (todos los consultorios sin horario ese día, o sin consultorios)."}
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
          <strong>Sin horario ese día ({data.rooms_without_hours.length}):</strong>{" "}
          {data.rooms_without_hours.map((r) => r.code).join(", ")}
          <div style={{ fontSize: 12, marginTop: 4, color: uiTheme.colors.textMuted }}>
            No entran en el denominador ni en la torta. Configurá franjas en Horarios consultorio.
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
