import { useCallback, useEffect, useMemo, useState } from "react";
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import {
  aggregateTurnosResumen,
  filterOccupancyForIndicadores,
  monthDateRange,
  occupancyHorarioIds,
} from "../lib/ocupacionIndicators";
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

const metricGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
  gap: 10,
};

export function IndicadoresOcupacionPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [periodMode, setPeriodMode] = useState("day");
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

  const [occupancyItems, setOccupancyItems] = useState([]);
  const [roomAgendaIds, setRoomAgendaIds] = useState(null);

  const [resumenRaw, setResumenRaw] = useState(null);
  const [resumenLoading, setResumenLoading] = useState(false);
  const [resumenError, setResumenError] = useState("");

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
    (async () => {
      try {
        const occ = await apiRequestWithRefresh("/distribucion/ocupacion/horarios-activos");
        setOccupancyItems(Array.isArray(occ?.items) ? occ.items : []);
      } catch {
        setOccupancyItems([]);
      }
    })();
  }, []);

  const roomsForSelect = useMemo(() => {
    if (!locationId) return rooms;
    return rooms.filter((r) => String(r.location_id) === String(locationId));
  }, [rooms, locationId]);

  const pieDate = periodMode === "month" ? `${month}-01` : day;

  const load = useCallback(async () => {
    if (!pieDate || pieDate.length < 10) return;
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ date: pieDate });
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
  }, [pieDate, locationId, roomId, especialidad, medico]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (roomId && !roomsForSelect.some((r) => String(r.id) === String(roomId))) {
      setRoomId("");
    }
  }, [roomsForSelect, roomId]);

  useEffect(() => {
    if (!roomId) {
      setRoomAgendaIds(null);
      return undefined;
    }
    let cancelled = false;
    (async () => {
      try {
        const data = await apiRequestWithRefresh(`/consulting-rooms/${roomId}/id-agendas`);
        if (cancelled) return;
        const ids = new Set(
          (Array.isArray(data?.items) ? data.items : [])
            .map((item) => Number(item.id_agenda))
            .filter((id) => Number.isFinite(id) && id > 0)
        );
        setRoomAgendaIds(ids);
      } catch {
        if (!cancelled) setRoomAgendaIds(new Set());
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [roomId]);

  const resumenRange = useMemo(() => {
    if (periodMode === "month") return monthDateRange(month);
    if (!day) return null;
    return { fecha_desde: day, fecha_hasta: day };
  }, [periodMode, day, month]);

  useEffect(() => {
    if (!resumenRange) return undefined;
    let cancelled = false;
    (async () => {
      setResumenLoading(true);
      setResumenError("");
      try {
        const params = new URLSearchParams({
          fecha_desde: resumenRange.fecha_desde,
          fecha_hasta: resumenRange.fecha_hasta,
        });
        const result = await apiRequestWithRefresh(
          `/distribucion/ocupacion/indicadores/turnos-resumen?${params}`
        );
        if (!cancelled) setResumenRaw(result);
      } catch (err) {
        if (!cancelled) {
          setResumenRaw(null);
          setResumenError(err.message || "No se pudo cargar el resumen de turnos");
        }
      } finally {
        if (!cancelled) setResumenLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [resumenRange]);

  const selectedLocation = useMemo(
    () => (locationId ? locations.find((loc) => String(loc.id) === String(locationId)) : null),
    [locations, locationId]
  );

  const filteredOccupancy = useMemo(
    () =>
      filterOccupancyForIndicadores(occupancyItems, {
        location: selectedLocation || null,
        // Mientras cargan agendas del consultorio, no matchear todo el dominio.
        roomAgendaIds: roomId ? roomAgendaIds ?? new Set() : null,
        especialidad: especialidad || null,
        medico: medico || null,
      }),
    [occupancyItems, selectedLocation, roomId, roomAgendaIds, especialidad, medico]
  );

  const horarioIds = useMemo(() => occupancyHorarioIds(filteredOccupancy), [filteredOccupancy]);

  const resumenAgg = useMemo(() => {
    if (!resumenRaw) return null;
    return aggregateTurnosResumen(resumenRaw.detalle, horarioIds);
  }, [resumenRaw, horarioIds]);

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
          Período
          <select
            value={periodMode}
            onChange={(e) => setPeriodMode(e.target.value)}
            style={filterSelect}
          >
            <option value="day">Día</option>
            <option value="month">Mes</option>
          </select>
        </label>
        {periodMode === "day" ? (
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

      <div
        style={{
          marginTop: 24,
          padding: "14px 16px",
          borderRadius: uiTheme.radius.md,
          border: `1px solid ${uiTheme.colors.border}`,
          background: uiTheme.colors.surface,
        }}
      >
        <h2 style={{ margin: "0 0 6px", fontSize: "1.05rem", color: uiTheme.colors.text }}>
          Resumen de turnos
        </h2>
        <p style={{ ...uiStyles.helpText, marginTop: 0, marginBottom: 12 }}>
          Join por <code>turno_horario_id</code> = <code>id</code> de ocupación. Se descarga al cambiar día/mes;
          ubicación/consultorio/especialidad/médico solo reclasifican en memoria.
          {resumenRange
            ? ` Rango: ${resumenRange.fecha_desde} → ${resumenRange.fecha_hasta}.`
            : ""}
        </p>

        {resumenLoading ? (
          <p style={{ fontSize: 13, color: uiTheme.colors.textMuted, margin: 0 }}>Cargando resumen…</p>
        ) : null}
        {resumenError ? (
          <p style={{ color: uiTheme.colors.danger, fontSize: 13, margin: 0 }}>{resumenError}</p>
        ) : null}
        {!resumenLoading && !resumenError && resumenAgg ? (
          resumenAgg.matched_rows === 0 && resumenAgg.total_turnos === 0 ? (
            <p style={{ fontSize: 13, color: uiTheme.colors.textMuted, margin: 0 }}>
              Sin filas de resumen para el filtro actual (revisá ids en Ocupación tras Actualizar).
            </p>
          ) : (
            <div style={metricGrid}>
              {[
                ["Total turnos", resumenAgg.total_turnos],
                ["Pendientes", `${resumenAgg.turnos_pendientes} (${resumenAgg.porcentaje_pendientes}%)`],
                ["Confirmados", `${resumenAgg.turnos_confirmados} (${resumenAgg.porcentaje_confirmados}%)`],
                ["Cancelados", `${resumenAgg.turnos_cancelados} (${resumenAgg.porcentaje_cancelados}%)`],
                ["Atendidos", `${resumenAgg.turnos_atendidos} (${resumenAgg.porcentaje_atendidos}%)`],
                ["Ausentes", `${resumenAgg.turnos_ausentes} (${resumenAgg.porcentaje_ausentes}%)`],
                ["Espera promedio (días)", resumenAgg.espera_promedio_dias],
                ["Horarios matched", resumenAgg.matched_rows],
              ].map(([label, value]) => (
                <div key={label} style={{ ...uiStyles.listCard, padding: 12 }}>
                  <div style={{ fontSize: 11, color: uiTheme.colors.textMuted }}>{label}</div>
                  <div style={{ fontSize: 18, fontWeight: 650 }}>{value}</div>
                </div>
              ))}
            </div>
          )
        ) : null}
      </div>
    </section>
  );
}
