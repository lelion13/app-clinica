import { useCallback, useEffect, useMemo, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

const HOUR_START = 6;
const HOUR_END = 22;
const PX_PER_HOUR = 48;

function isoDate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function addDays(iso, n) {
  const d = new Date(`${iso}T12:00:00`);
  d.setDate(d.getDate() + n);
  return isoDate(d);
}

function parseLocalDateTime(value) {
  // "2026-08-03T09:00:00"
  const [datePart, timePart = "00:00:00"] = String(value).split("T");
  const [y, m, day] = datePart.split("-").map(Number);
  const [hh, mm, ss] = timePart.split(":").map(Number);
  return new Date(y, m - 1, day, hh || 0, mm || 0, ss || 0);
}

function minutesFromDayStart(dt) {
  return dt.getHours() * 60 + dt.getMinutes() + dt.getSeconds() / 60;
}

function Popover({ anchor, detail, onClose }) {
  if (!anchor || !detail) return null;
  const rows = [
    ["Consultorio", detail.room_code || (detail.room_id ? `#${detail.room_id}` : "Sin consultorio")],
    ["Ubicación", detail.location_name],
    ["id_dominio", detail.id_dominio],
    ["id_agenda", detail.id_agenda],
    ["tipo", detail.tipo],
    ["especialidad_agenda", detail.especialidad_agenda],
    ["medico", detail.medico],
    ["especialidad", detail.especialidad],
    ["dia", detail.dia],
    ["fecha_desde", detail.fecha_desde],
    ["hora_desde", detail.hora_desde],
    ["fecha_hasta", detail.fecha_hasta],
    ["hora_hasta", detail.hora_hasta],
    ["duracion_turno", detail.duracion_turno],
    ["cantidad_turnos", detail.cantidad_turnos],
    ["cantidad_sobreturno", detail.cantidad_sobreturno],
    ["id_dato", detail.id_dato],
  ];

  return (
    <div
      role="dialog"
      style={{
        position: "fixed",
        left: Math.min(anchor.x, window.innerWidth - 320),
        top: Math.min(anchor.y, window.innerHeight - 360),
        zIndex: 50,
        width: 300,
        maxHeight: 340,
        overflowY: "auto",
        background: uiTheme.colors.surface,
        border: `1px solid ${uiTheme.colors.borderStrong}`,
        borderRadius: uiTheme.radius.md,
        boxShadow: "0 12px 32px rgba(0,0,0,0.18)",
        padding: 12,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <strong style={{ fontSize: 13 }}>Detalle</strong>
        <button type="button" onClick={onClose} style={{ ...uiStyles.buttonSecondary, padding: "2px 8px" }}>
          Cerrar
        </button>
      </div>
      <dl style={{ margin: 0, display: "grid", gap: 6, fontSize: 12 }}>
        {rows.map(([k, v]) =>
          v === null || v === undefined || v === "" ? null : (
            <div key={k}>
              <dt style={{ color: uiTheme.colors.textMuted, margin: 0 }}>{k}</dt>
              <dd style={{ margin: "2px 0 0", color: uiTheme.colors.text }}>{String(v)}</dd>
            </div>
          )
        )}
      </dl>
    </div>
  );
}

export function AgendaOcupacionPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState([]);
  const [locationId, setLocationId] = useState("");
  const [day, setDay] = useState(() => isoDate(new Date()));
  const [events, setEvents] = useState([]);
  const [resources, setResources] = useState([]);
  const [popover, setPopover] = useState({ anchor: null, detail: null });

  useEffect(() => {
    safeLoad("/locations", setLocations, setError);
  }, []);

  const loadEvents = useCallback(async () => {
    if (!day) return;
    setError("");
    setLoading(true);
    try {
      const next = addDays(day, 1);
      const params = new URLSearchParams({ start: day, end: next });
      if (locationId) params.set("location_id", locationId);
      const data = await apiRequestWithRefresh(`/distribucion/ocupacion/agenda/events?${params}`);
      setEvents(Array.isArray(data?.events) ? data.events : []);
      setResources(Array.isArray(data?.resources) ? data.resources : []);
    } catch (err) {
      setEvents([]);
      setResources([]);
      setError(err.message || "No se pudieron cargar eventos");
    } finally {
      setLoading(false);
    }
  }, [day, locationId]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const hours = useMemo(() => {
    const list = [];
    for (let h = HOUR_START; h < HOUR_END; h += 1) list.push(h);
    return list;
  }, []);

  const gridHeight = (HOUR_END - HOUR_START) * PX_PER_HOUR;

  const eventsByResource = useMemo(() => {
    const map = {};
    for (const res of resources) map[res.id] = [];
    for (const ev of events) {
      const key = ev.resource_id || "unassigned";
      if (!map[key]) map[key] = [];
      map[key].push(ev);
    }
    return map;
  }, [events, resources]);

  const dayLabel = useMemo(() => {
    try {
      return new Date(`${day}T12:00:00`).toLocaleDateString("es-AR", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
      });
    } catch {
      return day;
    }
  }, [day]);

  return (
    <section>
      <div style={{ marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Agenda ocupación</h2>
        <p style={{ margin: "6px 0 0", color: uiTheme.colors.textMuted, fontSize: 13 }}>
          Grilla por consultorio (estilo planilla). Sync solo desde Ocupación. Mapeá agendas en Consultorios.
          {loading ? " Cargando…" : ""}
        </p>
      </div>

      {error ? <div style={{ ...uiStyles.alertError, marginBottom: 12 }}>{error}</div> : null}

      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 14, alignItems: "flex-end" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12 }}>
          Ubicación
          <select
            value={locationId}
            onChange={(e) => setLocationId(e.target.value)}
            style={uiStyles.formControl}
          >
            <option value="">Todas</option>
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12 }}>
          Día
          <input type="date" value={day} onChange={(e) => setDay(e.target.value)} style={uiStyles.formControl} />
        </label>
        <button type="button" style={uiStyles.buttonSecondary} onClick={() => setDay(addDays(day, -1))}>
          ←
        </button>
        <button type="button" style={uiStyles.buttonSecondary} onClick={() => setDay(isoDate(new Date()))}>
          Hoy
        </button>
        <button type="button" style={uiStyles.buttonSecondary} onClick={() => setDay(addDays(day, 1))}>
          →
        </button>
        <span style={{ fontSize: 13, color: uiTheme.colors.textMuted, textTransform: "capitalize" }}>{dayLabel}</span>
      </div>

      <div style={{ overflowX: "auto", border: `1px solid ${uiTheme.colors.border}`, borderRadius: uiTheme.radius.md }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `56px repeat(${Math.max(resources.length, 1)}, minmax(120px, 1fr))`,
            minWidth: 56 + Math.max(resources.length, 1) * 120,
          }}
        >
          <div
            style={{
              position: "sticky",
              left: 0,
              zIndex: 2,
              background: uiTheme.colors.surfaceMuted,
              borderBottom: `1px solid ${uiTheme.colors.borderStrong}`,
              borderRight: `1px solid ${uiTheme.colors.border}`,
              padding: 8,
              fontSize: 11,
              fontWeight: 600,
            }}
          >
            HORA
          </div>
          {resources.map((res) => (
            <div
              key={res.id}
              style={{
                background: uiTheme.colors.surfaceMuted,
                borderBottom: `1px solid ${uiTheme.colors.borderStrong}`,
                borderRight: `1px solid ${uiTheme.colors.border}`,
                padding: 8,
                fontSize: 12,
                fontWeight: 700,
                textAlign: "center",
              }}
            >
              {res.title}
            </div>
          ))}

          <div
            style={{
              position: "sticky",
              left: 0,
              zIndex: 1,
              background: uiTheme.colors.surface,
              borderRight: `1px solid ${uiTheme.colors.border}`,
              height: gridHeight,
            }}
          >
            {hours.map((h) => (
              <div
                key={h}
                style={{
                  height: PX_PER_HOUR,
                  borderBottom: `1px solid ${uiTheme.colors.border}`,
                  fontSize: 11,
                  color: uiTheme.colors.textMuted,
                  padding: "2px 6px",
                }}
              >
                {String(h).padStart(2, "0")}:00
              </div>
            ))}
          </div>

          {resources.map((res) => (
            <div
              key={res.id}
              style={{
                position: "relative",
                height: gridHeight,
                borderRight: `1px solid ${uiTheme.colors.border}`,
                background:
                  res.id === "unassigned"
                    ? "repeating-linear-gradient(135deg, transparent, transparent 6px, rgba(0,0,0,0.03) 6px, rgba(0,0,0,0.03) 12px)"
                    : uiTheme.colors.surface,
              }}
            >
              {hours.map((h) => (
                <div
                  key={h}
                  style={{
                    position: "absolute",
                    left: 0,
                    right: 0,
                    top: (h - HOUR_START) * PX_PER_HOUR,
                    height: PX_PER_HOUR,
                    borderBottom: `1px solid ${uiTheme.colors.border}`,
                    pointerEvents: "none",
                  }}
                />
              ))}
              {(eventsByResource[res.id] || []).map((ev) => {
                const startDt = parseLocalDateTime(ev.start);
                const endDt = parseLocalDateTime(ev.end);
                const topMin = minutesFromDayStart(startDt) - HOUR_START * 60;
                const endMin = minutesFromDayStart(endDt) - HOUR_START * 60;
                const top = Math.max(0, (topMin / 60) * PX_PER_HOUR);
                const height = Math.max(18, ((endMin - topMin) / 60) * PX_PER_HOUR);
                return (
                  <button
                    key={ev.id}
                    type="button"
                    title={ev.title}
                    onClick={(e) => {
                      const rect = e.currentTarget.getBoundingClientRect();
                      setPopover({
                        anchor: { x: rect.left, y: rect.bottom + 4 },
                        detail: ev.extended || {},
                      });
                    }}
                    style={{
                      position: "absolute",
                      left: 3,
                      right: 3,
                      top,
                      height,
                      overflow: "hidden",
                      border: "none",
                      borderRadius: 4,
                      background: uiTheme.colors.primary,
                      color: "#fff",
                      fontSize: 11,
                      fontWeight: 600,
                      textAlign: "left",
                      padding: "4px 6px",
                      cursor: "pointer",
                      lineHeight: 1.25,
                    }}
                  >
                    {ev.title || "(sin médico)"}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {!resources.length && !loading ? (
        <p style={{ marginTop: 12, color: uiTheme.colors.textMuted, fontSize: 13 }}>
          No hay columnas. Creá consultorios en la ubicación o dejá “Todas”.
        </p>
      ) : null}

      <Popover
        anchor={popover.anchor}
        detail={popover.detail}
        onClose={() => setPopover({ anchor: null, detail: null })}
      />
    </section>
  );
}
