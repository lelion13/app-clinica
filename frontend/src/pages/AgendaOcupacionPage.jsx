import { useCallback, useEffect, useMemo, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

const HOUR_START = 6;
const HOUR_END = 22;
const PX_PER_HOUR = 48;
const HOUR_COL_PX = 56;
const COL_MIN_PX = 160;
const HEADER_H = 36;

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
  const [datePart, timePart = "00:00:00"] = String(value).split("T");
  const [y, m, day] = datePart.split("-").map(Number);
  const [hh, mm, ss] = timePart.split(":").map(Number);
  return new Date(y, m - 1, day, hh || 0, mm || 0, ss || 0);
}

function minutesFromDayStart(dt) {
  return dt.getHours() * 60 + dt.getMinutes() + dt.getSeconds() / 60;
}

function toggleValue(list, value) {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value];
}

function MultiFilter({ label, options, selected, onChange }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, minWidth: 140 }}>
      {label}
      <div
        style={{
          ...uiStyles.formControl,
          height: "auto",
          maxHeight: 110,
          overflowY: "auto",
          padding: 6,
          display: "flex",
          flexDirection: "column",
          gap: 4,
          minWidth: 160,
        }}
      >
        {!options.length ? (
          <span style={{ color: uiTheme.colors.textMuted, fontSize: 11 }}>Sin opciones</span>
        ) : (
          options.map((opt) => {
            const value = opt.value;
            const checked = selected.includes(value);
            return (
              <label
                key={value}
                style={{
                  display: "flex",
                  gap: 6,
                  alignItems: "flex-start",
                  fontSize: 11,
                  cursor: "pointer",
                  lineHeight: 1.3,
                }}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => onChange(toggleValue(selected, value))}
                  style={{ marginTop: 1 }}
                />
                <span>{opt.label || value}</span>
              </label>
            );
          })
        )}
      </div>
      {selected.length ? (
        <span style={{ fontSize: 10, color: uiTheme.colors.textMuted }}>{selected.length} seleccionado(s)</span>
      ) : null}
    </label>
  );
}

function DetailModal({ detail, onClose }) {
  useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!detail) return null;

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
      role="presentation"
      onClick={onClose}
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
        aria-label="Detalle de agenda"
        onClick={(event) => event.stopPropagation()}
        style={{
          width: "min(420px, 100%)",
          maxHeight: "min(80vh, 520px)",
          overflowY: "auto",
          background: uiTheme.colors.surface,
          border: `1px solid ${uiTheme.colors.borderStrong}`,
          borderRadius: uiTheme.radius.md,
          boxShadow: "0 16px 40px rgba(0,0,0,0.22)",
          padding: 16,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10, gap: 8 }}>
          <strong style={{ fontSize: 14 }}>Detalle</strong>
          <button type="button" onClick={onClose} style={{ ...uiStyles.buttonSecondary, padding: "2px 10px" }}>
            Cerrar
          </button>
        </div>
        <dl style={{ margin: 0, display: "grid", gap: 8, fontSize: 12 }}>
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
  const [modalDetail, setModalDetail] = useState(null);
  const [filterOptions, setFilterOptions] = useState({ tipo: [], especialidad: [], medico: [] });
  const [tipos, setTipos] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [medicos, setMedicos] = useState([]);

  useEffect(() => {
    safeLoad("/locations", setLocations, setError);
    (async () => {
      try {
        const data = await apiRequestWithRefresh("/distribucion/ocupacion/agenda/filter-options");
        setFilterOptions({
          tipo: Array.isArray(data?.tipo) ? data.tipo : [],
          especialidad: Array.isArray(data?.especialidad) ? data.especialidad : [],
          medico: Array.isArray(data?.medico) ? data.medico : [],
        });
      } catch (err) {
        setError(err.message || "No se pudieron cargar opciones de filtro");
      }
    })();
  }, []);

  const loadEvents = useCallback(async () => {
    if (!day) return;
    setError("");
    setLoading(true);
    try {
      const next = addDays(day, 1);
      const params = new URLSearchParams({ start: day, end: next });
      if (locationId) params.set("location_id", locationId);
      for (const value of tipos) params.append("tipo", value);
      for (const value of especialidades) params.append("especialidad", value);
      for (const value of medicos) params.append("medico", value);
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
  }, [day, locationId, tipos, especialidades, medicos]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const hours = useMemo(() => {
    const list = [];
    for (let h = HOUR_START; h < HOUR_END; h += 1) list.push(h);
    return list;
  }, []);

  const gridHeight = (HOUR_END - HOUR_START) * PX_PER_HOUR;
  const displayResources = resources.length ? resources : [{ id: "_empty", title: "—" }];
  const colCount = displayResources.length;

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

  const stickyHeaderBase = {
    position: "sticky",
    top: 0,
    zIndex: 3,
    background: uiTheme.colors.surfaceMuted,
    borderBottom: `1px solid ${uiTheme.colors.borderStrong}`,
    borderRight: `1px solid ${uiTheme.colors.border}`,
    height: HEADER_H,
    boxSizing: "border-box",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "0 8px",
    fontSize: 12,
    fontWeight: 700,
  };

  return (
    <section
      style={{
        width: "100vw",
        marginLeft: "calc(50% - 50vw)",
        height: "calc(100dvh - 128px)",
        display: "flex",
        flexDirection: "column",
        boxSizing: "border-box",
        padding: "0 12px 8px",
        gap: 10,
      }}
    >
      <div style={{ flexShrink: 0 }}>
        <h2 style={{ margin: 0, fontSize: "1.25rem" }}>Agenda ocupación</h2>
        <p style={{ margin: "4px 0 0", color: uiTheme.colors.textMuted, fontSize: 13 }}>
          Grilla por consultorio. Sync solo desde Ocupación. Mapeá agendas en Consultorios.
          {loading ? " Cargando…" : ""}
        </p>
      </div>

      {error ? <div style={{ ...uiStyles.alertError, flexShrink: 0 }}>{error}</div> : null}

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 10,
          alignItems: "flex-end",
          flexShrink: 0,
        }}
      >
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
                {loc.tipo ? ` · ${loc.tipo}` : ""}
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
        <MultiFilter label="Tipo" options={filterOptions.tipo} selected={tipos} onChange={setTipos} />
        <MultiFilter
          label="Especialidad"
          options={filterOptions.especialidad}
          selected={especialidades}
          onChange={setEspecialidades}
        />
        <MultiFilter label="Médico" options={filterOptions.medico} selected={medicos} onChange={setMedicos} />
        {tipos.length || especialidades.length || medicos.length ? (
          <button
            type="button"
            style={uiStyles.buttonSecondary}
            onClick={() => {
              setTipos([]);
              setEspecialidades([]);
              setMedicos([]);
            }}
          >
            Limpiar filtros
          </button>
        ) : null}
      </div>

      <div
        style={{
          flex: 1,
          minHeight: 0,
          overflow: "auto",
          border: `1px solid ${uiTheme.colors.border}`,
          borderRadius: uiTheme.radius.md,
          background: uiTheme.colors.surface,
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `${HOUR_COL_PX}px repeat(${colCount}, minmax(${COL_MIN_PX}px, 1fr))`,
            minWidth: HOUR_COL_PX + colCount * COL_MIN_PX,
          }}
        >
          <div
            style={{
              ...stickyHeaderBase,
              left: 0,
              zIndex: 5,
              justifyContent: "flex-start",
              fontSize: 11,
              fontWeight: 600,
            }}
          >
            HORA
          </div>
          {displayResources.map((res) => (
            <div key={`h-${res.id}`} style={stickyHeaderBase}>
              {res.title}
            </div>
          ))}

          <div
            style={{
              position: "sticky",
              left: 0,
              zIndex: 2,
              background: uiTheme.colors.surface,
              borderRight: `1px solid ${uiTheme.colors.border}`,
              height: gridHeight,
              boxSizing: "border-box",
              /* relative + sticky: absolute hour marks share coords with resource columns */
            }}
          >
            <div style={{ position: "relative", height: gridHeight, width: "100%" }}>
              {hours.map((h) => (
                <div
                  key={h}
                  style={{
                    position: "absolute",
                    left: 0,
                    right: 0,
                    top: (h - HOUR_START) * PX_PER_HOUR,
                    height: PX_PER_HOUR,
                    boxSizing: "border-box",
                    borderBottom: `1px solid ${uiTheme.colors.border}`,
                    fontSize: 11,
                    color: uiTheme.colors.textMuted,
                    padding: "2px 6px",
                    lineHeight: 1.2,
                  }}
                >
                  {String(h).padStart(2, "0")}:00
                </div>
              ))}
            </div>
          </div>

          {displayResources.map((res) => (
            <div
              key={res.id}
              style={{
                position: "relative",
                height: gridHeight,
                borderRight: `1px solid ${uiTheme.colors.border}`,
                boxSizing: "border-box",
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
                    boxSizing: "border-box",
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
                    onClick={() => setModalDetail(ev.extended || {})}
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
        <p style={{ margin: 0, color: uiTheme.colors.textMuted, fontSize: 13, flexShrink: 0 }}>
          No hay columnas. Creá consultorios en la ubicación o dejá “Todas”.
        </p>
      ) : null}

      <DetailModal detail={modalDetail} onClose={() => setModalDetail(null)} />
    </section>
  );
}
