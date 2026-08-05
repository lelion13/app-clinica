import { useCallback, useEffect, useRef, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import esLocale from "@fullcalendar/core/locales/es";

import { apiRequestWithRefresh } from "../services/api";
import { uiStyles, uiTheme } from "../ui/theme";

const FILTER_KEYS = [
  { key: "id_dominio", label: "Ubicación" },
  { key: "tipo", label: "Tipo" },
  { key: "especialidad", label: "Especialidad" },
  { key: "medico", label: "Médico" },
  { key: "dia", label: "Día" },
];

function emptyFilters() {
  return Object.fromEntries(FILTER_KEYS.map((f) => [f.key, []]));
}

function isoDate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function MultiFilter({ label, options, selected, onChange }) {
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
    if (selected.includes(token)) onChange(selected.filter((v) => v !== token));
    else onChange([...selected, token]);
  };

  return (
    <div ref={rootRef} style={{ position: "relative", minWidth: 140 }}>
      <div style={{ fontSize: 11, color: uiTheme.colors.textMuted, marginBottom: 4 }}>{label}</div>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        style={{
          ...uiStyles.buttonSecondary,
          width: "100%",
          padding: "6px 10px",
          fontSize: 12,
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
            zIndex: 40,
            minWidth: 200,
            maxHeight: 240,
            overflowY: "auto",
            background: uiTheme.colors.surface,
            border: `1px solid ${uiTheme.colors.border}`,
            borderRadius: uiTheme.radius.sm,
            boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
            padding: 8,
          }}
        >
          {(options || []).length === 0 ? (
            <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Sin opciones</div>
          ) : (
            options.map((opt) => (
              <label
                key={opt.value}
                style={{
                  display: "flex",
                  gap: 8,
                  alignItems: "flex-start",
                  fontSize: 12,
                  padding: "4px 2px",
                  cursor: "pointer",
                }}
              >
                <input
                  type="checkbox"
                  checked={selected.includes(opt.value)}
                  onChange={() => toggle(opt.value)}
                />
                <span>{opt.label}</span>
              </label>
            ))
          )}
        </div>
      ) : null}
    </div>
  );
}

function Popover({ anchor, detail, onClose }) {
  if (!anchor || !detail) return null;
  const rows = [
    ["Ubicación", detail.location_name],
    ["id_dominio", detail.id_dominio],
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
  const [events, setEvents] = useState([]);
  const [filterOptions, setFilterOptions] = useState({
    id_dominio: [],
    tipo: [],
    especialidad: [],
    medico: [],
    dia: [],
  });
  const [filters, setFilters] = useState(emptyFilters);
  const [range, setRange] = useState({ start: null, end: null });
  const [popover, setPopover] = useState({ anchor: null, detail: null });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await apiRequestWithRefresh("/distribucion/ocupacion/agenda/filter-options");
        if (!cancelled) setFilterOptions(data || {});
      } catch (err) {
        if (!cancelled) setError(err.message || "No se pudieron cargar filtros");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const loadEvents = useCallback(async (nextRange, nextFilters) => {
    if (!nextRange?.start || !nextRange?.end) return;
    setError("");
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("start", nextRange.start);
      params.set("end", nextRange.end);
      for (const { key } of FILTER_KEYS) {
        for (const value of nextFilters[key] || []) {
          params.append(key, value);
        }
      }
      const data = await apiRequestWithRefresh(
        `/distribucion/ocupacion/agenda/events?${params.toString()}`
      );
      const mapped = (data?.events || []).map((ev) => ({
        id: ev.id,
        title: ev.title || "(sin médico)",
        start: ev.start,
        end: ev.end,
        backgroundColor: uiTheme.colors.primary,
        borderColor: uiTheme.colors.primary,
        extendedProps: ev.extended || {},
      }));
      setEvents(mapped);
    } catch (err) {
      setEvents([]);
      setError(err.message || "No se pudieron cargar eventos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!range.start || !range.end) return;
    loadEvents(range, filters);
  }, [range, filters, loadEvents]);

  const onDatesSet = (arg) => {
    const start = isoDate(arg.start);
    const end = isoDate(arg.end);
    setRange((prev) => (prev.start === start && prev.end === end ? prev : { start, end }));
  };

  const activeFilterCount = FILTER_KEYS.reduce((acc, f) => acc + (filters[f.key]?.length ? 1 : 0), 0);

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginBottom: 8 }}>
        <div>
          <h2 style={{ margin: 0 }}>Agenda ocupación</h2>
          <p style={{ margin: "6px 0 0", color: uiTheme.colors.textMuted, fontSize: 13 }}>
            Vista read-only del sync de Ocupación. Filtrá y navegá el calendario. Sync solo desde Ocupación.
            {loading ? " Cargando…" : ""}
          </p>
        </div>
        <button
          type="button"
          style={uiStyles.buttonSecondary}
          onClick={() => setFilters(emptyFilters())}
          disabled={!activeFilterCount}
        >
          Limpiar filtros
        </button>
      </div>

      {error ? (
        <div style={{ ...uiStyles.alertError, marginBottom: 12 }}>{error}</div>
      ) : null}

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 12,
          marginBottom: 16,
          padding: 12,
          background: uiTheme.colors.surfaceMuted,
          borderRadius: uiTheme.radius.md,
        }}
      >
        {FILTER_KEYS.map((f) => (
          <MultiFilter
            key={f.key}
            label={f.label}
            options={filterOptions[f.key] || []}
            selected={filters[f.key] || []}
            onChange={(next) => setFilters((prev) => ({ ...prev, [f.key]: next }))}
          />
        ))}
      </div>

      <FullCalendar
        plugins={[timeGridPlugin, dayGridPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: "prev,next today",
          center: "title",
          right: "timeGridDay,timeGridWeek,dayGridMonth",
        }}
        datesSet={onDatesSet}
        events={events}
        eventClick={(info) => {
          const rect = info.el.getBoundingClientRect();
          setPopover({
            anchor: { x: rect.left, y: rect.bottom + 6 },
            detail: info.event.extendedProps || {},
          });
        }}
        height={650}
        locale={esLocale}
        allDaySlot={false}
        slotMinTime="06:00:00"
        slotMaxTime="22:00:00"
        editable={false}
        selectable={false}
      />

      <Popover
        anchor={popover.anchor}
        detail={popover.detail}
        onClose={() => setPopover({ anchor: null, detail: null })}
      />
    </section>
  );
}
