import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

const HOUR_START = 6;
const HOUR_END = 22;
const PX_PER_HOUR = 48;
const HOUR_COL_PX = 56;
const COL_MIN_PX = 160;
const HEADER_H = 36;
const DND_MIME = "application/x-agenda-id";

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

const filterFieldStyle = {
  display: "flex",
  flexDirection: "column",
  gap: 2,
  fontSize: 11,
  flex: "0 1 auto",
  minWidth: 0,
};

const filterSelectStyle = {
  ...uiStyles.formControl,
  minWidth: 120,
  maxWidth: 200,
  fontSize: 13,
  padding: "6px 8px",
};

function FilterSelect({ label, value, onChange, options, allLabel = "Todos" }) {
  return (
    <label style={filterFieldStyle}>
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)} style={filterSelectStyle}>
        <option value="">{allLabel}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label || opt.value}
          </option>
        ))}
      </select>
    </label>
  );
}

function ModalShell({ title, onClose, children, footer }) {
  useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

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
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
        style={{
          width: "min(440px, 100%)",
          maxHeight: "min(80vh, 560px)",
          overflowY: "auto",
          background: uiTheme.colors.surface,
          border: `1px solid ${uiTheme.colors.borderStrong}`,
          borderRadius: uiTheme.radius.md,
          boxShadow: "0 16px 40px rgba(0,0,0,0.22)",
          padding: 16,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10, gap: 8 }}>
          <strong style={{ fontSize: 14 }}>{title}</strong>
          <button type="button" onClick={onClose} style={{ ...uiStyles.buttonSecondary, padding: "2px 10px" }}>
            Cerrar
          </button>
        </div>
        {children}
        {footer ? <div style={{ marginTop: 14, display: "flex", justifyContent: "flex-end", gap: 8 }}>{footer}</div> : null}
      </div>
    </div>
  );
}

function DetailModal({ detail, onClose }) {
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
    <ModalShell title="Detalle" onClose={onClose}>
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
    </ModalShell>
  );
}

function formatReassignError(err) {
  const detail = err?.detail;
  if (!detail || typeof detail !== "object") {
    return { title: "No se pudo mover", body: err?.message || "Error inesperado" };
  }
  const conflicts = Array.isArray(detail.conflicts) ? detail.conflicts : [];
  const lines = conflicts.length
    ? conflicts.map((c) => c.message || JSON.stringify(c))
    : [detail.message || err.message || "Error de validación"];
  return {
    title: "No se pudo asignar",
    body: lines.join("\n"),
  };
}

export function AgendaOcupacionPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [locations, setLocations] = useState([]);
  const [locationId, setLocationId] = useState("");
  const [day, setDay] = useState(() => isoDate(new Date()));
  const [events, setEvents] = useState([]);
  const [resources, setResources] = useState([]);
  const [modalDetail, setModalDetail] = useState(null);
  const [filterOptions, setFilterOptions] = useState({ tipo: [], especialidad: [], medico: [] });
  const [tipo, setTipo] = useState("");
  const [especialidad, setEspecialidad] = useState("");
  const [medico, setMedico] = useState("");
  const [dragOverId, setDragOverId] = useState(null);
  const [confirmMove, setConfirmMove] = useState(null);
  const [confirmUnassign, setConfirmUnassign] = useState(null);
  const [errorModal, setErrorModal] = useState(null);
  const suppressClickRef = useRef(false);

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
      if (tipo) params.append("tipo", tipo);
      if (especialidad) params.append("especialidad", especialidad);
      if (medico) params.append("medico", medico);
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
  }, [day, locationId, tipo, especialidad, medico]);

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

  const doReassign = useCallback(
    async ({ id_agenda, target_room_id, confirm_move = false, confirm_unassign = false }) => {
      setBusy(true);
      setError("");
      try {
        await apiRequestWithRefresh("/distribucion/ocupacion/agenda/reassign", {
          method: "POST",
          body: JSON.stringify({
            id_agenda,
            target_room_id,
            confirm_move,
            confirm_unassign,
          }),
        });
        await loadEvents();
        return true;
      } catch (err) {
        if (err?.status === 409 && err?.detail?.requires_confirm_move) {
          setConfirmMove({
            id_agenda,
            target_room_id,
            current_room_code: err.detail.current_room_code,
            target_room_code: err.detail.target_room_code,
            message: err.detail.message || err.message,
          });
          return false;
        }
        setErrorModal(formatReassignError(err));
        return false;
      } finally {
        setBusy(false);
      }
    },
    [loadEvents]
  );

  const handleDropOnResource = useCallback(
    async (res, rawIdAgenda) => {
      const id_agenda = Number(rawIdAgenda);
      if (!Number.isFinite(id_agenda) || id_agenda <= 0) return;

      const isUnassigned = res.id === "unassigned";
      const target_room_id = isUnassigned ? null : res.room_id ?? Number(res.id);
      if (!isUnassigned && (!Number.isFinite(target_room_id) || target_room_id <= 0)) return;

      // Same column?
      const alreadyHere = events.some(
        (ev) =>
          Number(ev.extended?.id_agenda) === id_agenda &&
          (ev.resource_id || "unassigned") === res.id
      );
      if (alreadyHere) return;

      if (isUnassigned) {
        setConfirmUnassign({ id_agenda });
        return;
      }

      await doReassign({ id_agenda, target_room_id, confirm_move: false });
    },
    [doReassign, events]
  );

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

  const navBtn = { ...uiStyles.buttonSecondary, padding: "6px 10px", fontSize: 13 };

  return (
    <section
      style={{
        width: "100vw",
        marginLeft: "calc(50% - 50vw)",
        height: "calc(100dvh - 112px)",
        display: "flex",
        flexDirection: "column",
        boxSizing: "border-box",
        padding: "0 12px 6px",
        gap: 6,
      }}
    >
      <div
        style={{
          flexShrink: 0,
          display: "flex",
          alignItems: "baseline",
          gap: 10,
          flexWrap: "nowrap",
          minHeight: 0,
        }}
      >
        <h2 style={{ margin: 0, fontSize: "1.1rem", whiteSpace: "nowrap" }}>Agenda ocupación</h2>
        <span style={{ color: uiTheme.colors.textMuted, fontSize: 12, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          Sync desde Ocupación · Arrastrá bloques entre columnas
          {loading || busy ? " · Cargando…" : ""}
        </span>
      </div>

      {error ? (
        <div
          style={{
            flexShrink: 0,
            padding: "6px 10px",
            fontSize: 13,
            color: uiTheme.colors.danger,
            border: `1px solid ${uiTheme.colors.borderStrong}`,
            borderRadius: uiTheme.radius.sm,
            background: "#fff5f5",
          }}
        >
          {error}
        </div>
      ) : null}

      <div
        style={{
          display: "flex",
          flexWrap: "nowrap",
          gap: 8,
          alignItems: "flex-end",
          flexShrink: 0,
          overflowX: "auto",
          paddingBottom: 2,
        }}
      >
        <FilterSelect
          label="Ubicación"
          value={locationId}
          onChange={setLocationId}
          allLabel="Todas"
          options={locations.map((loc) => ({
            value: String(loc.id),
            label: `${loc.name}${loc.tipo ? ` · ${loc.tipo}` : ""}`,
          }))}
        />
        <label style={filterFieldStyle}>
          Día
          <input
            type="date"
            value={day}
            onChange={(e) => setDay(e.target.value)}
            style={{ ...filterSelectStyle, maxWidth: 150 }}
          />
        </label>
        <div style={{ display: "flex", gap: 4, alignItems: "center", paddingBottom: 1 }}>
          <button type="button" style={navBtn} onClick={() => setDay(addDays(day, -1))} aria-label="Día anterior">
            ←
          </button>
          <button type="button" style={navBtn} onClick={() => setDay(isoDate(new Date()))}>
            Hoy
          </button>
          <button type="button" style={navBtn} onClick={() => setDay(addDays(day, 1))} aria-label="Día siguiente">
            →
          </button>
        </div>
        <span
          style={{
            fontSize: 12,
            color: uiTheme.colors.textMuted,
            textTransform: "capitalize",
            whiteSpace: "nowrap",
            paddingBottom: 8,
          }}
        >
          {dayLabel}
        </span>
        <FilterSelect label="Tipo" value={tipo} onChange={setTipo} options={filterOptions.tipo} />
        <FilterSelect
          label="Especialidad"
          value={especialidad}
          onChange={setEspecialidad}
          options={filterOptions.especialidad}
        />
        <FilterSelect label="Médico" value={medico} onChange={setMedico} options={filterOptions.medico} />
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

          {displayResources.map((res) => {
            const canDrop = res.id !== "_empty";
            const isOver = dragOverId === res.id;
            return (
              <div
                key={res.id}
                onDragOver={
                  canDrop
                    ? (e) => {
                        e.preventDefault();
                        e.dataTransfer.dropEffect = "move";
                        setDragOverId(res.id);
                      }
                    : undefined
                }
                onDragLeave={
                  canDrop
                    ? () => {
                        setDragOverId((cur) => (cur === res.id ? null : cur));
                      }
                    : undefined
                }
                onDrop={
                  canDrop
                    ? (e) => {
                        e.preventDefault();
                        setDragOverId(null);
                        const raw = e.dataTransfer.getData(DND_MIME) || e.dataTransfer.getData("text/plain");
                        handleDropOnResource(res, raw);
                      }
                    : undefined
                }
                style={{
                  position: "relative",
                  height: gridHeight,
                  borderRight: `1px solid ${uiTheme.colors.border}`,
                  boxSizing: "border-box",
                  outline: isOver ? `2px solid ${uiTheme.colors.primary}` : "none",
                  outlineOffset: -2,
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
                  const idAgenda = ev.extended?.id_agenda;
                  const draggable = Number.isFinite(Number(idAgenda)) && Number(idAgenda) > 0 && !busy;
                  return (
                    <button
                      key={ev.id}
                      type="button"
                      title={ev.title}
                      draggable={draggable}
                      onDragStart={(e) => {
                        if (!draggable) return;
                        suppressClickRef.current = true;
                        e.dataTransfer.setData(DND_MIME, String(idAgenda));
                        e.dataTransfer.setData("text/plain", String(idAgenda));
                        e.dataTransfer.effectAllowed = "move";
                      }}
                      onDragEnd={() => setDragOverId(null)}
                      onClick={() => {
                        if (suppressClickRef.current) {
                          suppressClickRef.current = false;
                          return;
                        }
                        setModalDetail(ev.extended || {});
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
                        cursor: draggable ? "grab" : "pointer",
                        lineHeight: 1.25,
                        opacity: busy ? 0.7 : 1,
                      }}
                    >
                      {ev.title || "(sin médico)"}
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>

      {!resources.length && !loading ? (
        <p style={{ margin: 0, color: uiTheme.colors.textMuted, fontSize: 13, flexShrink: 0 }}>
          No hay columnas. Creá consultorios en la ubicación o dejá “Todas”.
        </p>
      ) : null}

      <DetailModal detail={modalDetail} onClose={() => setModalDetail(null)} />

      {confirmMove ? (
        <ModalShell
          title="Mover agenda"
          onClose={() => setConfirmMove(null)}
          footer={
            <>
              <button type="button" style={uiStyles.buttonSecondary} onClick={() => setConfirmMove(null)}>
                Cancelar
              </button>
              <button
                type="button"
                style={uiStyles.buttonPrimary}
                disabled={busy}
                onClick={async () => {
                  const payload = confirmMove;
                  setConfirmMove(null);
                  await doReassign({
                    id_agenda: payload.id_agenda,
                    target_room_id: payload.target_room_id,
                    confirm_move: true,
                  });
                }}
              >
                Mover
              </button>
            </>
          }
        >
          <p style={{ margin: 0, fontSize: 13, lineHeight: 1.45 }}>
            {confirmMove.message ||
              `Esta agenda está en ${confirmMove.current_room_code}. ¿Moverla a ${confirmMove.target_room_code}?`}
          </p>
          <p style={{ margin: "8px 0 0", fontSize: 12, color: uiTheme.colors.textMuted }}>
            Se reasignan todos los días de la agenda (id {confirmMove.id_agenda}).
          </p>
        </ModalShell>
      ) : null}

      {confirmUnassign ? (
        <ModalShell
          title="Quitar consultorio"
          onClose={() => setConfirmUnassign(null)}
          footer={
            <>
              <button type="button" style={uiStyles.buttonSecondary} onClick={() => setConfirmUnassign(null)}>
                Cancelar
              </button>
              <button
                type="button"
                style={uiStyles.buttonPrimary}
                disabled={busy}
                onClick={async () => {
                  const payload = confirmUnassign;
                  setConfirmUnassign(null);
                  await doReassign({
                    id_agenda: payload.id_agenda,
                    target_room_id: null,
                    confirm_unassign: true,
                  });
                }}
              >
                Desasignar
              </button>
            </>
          }
        >
          <p style={{ margin: 0, fontSize: 13, lineHeight: 1.45 }}>
            ¿Quitar el consultorio de esta agenda (id {confirmUnassign.id_agenda})? Pasará a{" "}
            <strong>Sin consultorio</strong> en todos los días.
          </p>
        </ModalShell>
      ) : null}

      {errorModal ? (
        <ModalShell title={errorModal.title} onClose={() => setErrorModal(null)}>
          <pre
            style={{
              margin: 0,
              whiteSpace: "pre-wrap",
              fontFamily: "inherit",
              fontSize: 13,
              lineHeight: 1.45,
              color: uiTheme.colors.text,
            }}
          >
            {errorModal.body}
          </pre>
        </ModalShell>
      ) : null}
    </section>
  );
}
