import { useCallback, useEffect, useMemo, useState } from "react";

import { ProfessionalCombobox, alignedNativeFormControlStyle } from "../components/ProfessionalCombobox";
import { safeLoad } from "../lib/apiHelpers";
import { apiRequestWithRefresh } from "../services/api";
import { uiStyles, uiTheme } from "../ui/theme";

const WEEKDAYS = [
  { value: 0, label: "Domingo" },
  { value: 1, label: "Lunes" },
  { value: 2, label: "Martes" },
  { value: 3, label: "Miércoles" },
  { value: 4, label: "Jueves" },
  { value: 5, label: "Viernes" },
  { value: 6, label: "Sábado" },
];

const SLOT_START_HOUR = 6;
const SLOT_END_HOUR = 22;

function timeToMinutes(timeLike) {
  if (!timeLike) return 0;
  const [h, m] = String(timeLike).split(":");
  return Number(h) * 60 + Number(m);
}

function minutesToTime(minutes) {
  const h = String(Math.floor(minutes / 60)).padStart(2, "0");
  const m = String(minutes % 60).padStart(2, "0");
  return `${h}:${m}`;
}

function buildHalfHourSlots(startHour = SLOT_START_HOUR, endHour = SLOT_END_HOUR) {
  const slots = [];
  for (let m = startHour * 60; m < endHour * 60; m += 30) {
    slots.push({
      key: minutesToTime(m),
      start: m,
      end: m + 30,
    });
  }
  return slots;
}

function inRange(slot, startTime, endTime) {
  const a = timeToMinutes(startTime);
  const b = timeToMinutes(endTime);
  return slot.start >= a && slot.end <= b;
}

/** Texto largo en celdas angostas: varias líneas + clamp; nombre completo en `title` del td. */
const slotCellNameStyle = {
  display: "-webkit-box",
  WebkitBoxOrient: "vertical",
  WebkitLineClamp: 4,
  overflow: "hidden",
  wordBreak: "break-word",
  overflowWrap: "break-word",
  hyphens: "auto",
  lineHeight: 1.25,
  maxWidth: "100%",
  margin: "0 auto",
};

const formFieldLabelStyle = {
  display: "flex",
  flexDirection: "column",
  gap: 4,
  fontSize: 13,
  color: uiTheme.colors.textMuted,
};

const weekdayButtonBaseStyle = {
  border: `1px solid ${uiTheme.colors.borderStrong}`,
  borderRadius: uiTheme.radius.sm,
  padding: "6px 10px",
  cursor: "pointer",
  transition: "background-color 140ms ease, color 140ms ease, border-color 140ms ease",
};

/** Ancho fijo de la columna de hora; el resto del ancho va a los consultorios. */
const SCHEDULE_COL_WIDTH_PX = 72;

export function WeeklyOccupancyPage() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [professionals, setProfessionals] = useState([]);
  const [roomHoursByRoom, setRoomHoursByRoom] = useState({});
  const [assignments, setAssignments] = useState([]);
  const [conflictBlocks, setConflictBlocks] = useState([]);

  const [selectedLocationId, setSelectedLocationId] = useState("");
  const [selectedProfessionalId, setSelectedProfessionalId] = useState("");
  const [selectedWeekday, setSelectedWeekday] = useState(1);

  const [formRoomId, setFormRoomId] = useState("");
  const [formProfessionalId, setFormProfessionalId] = useState("");
  const [formWeekday, setFormWeekday] = useState(1);
  const [formStartTime, setFormStartTime] = useState("08:00");
  const [formEndTime, setFormEndTime] = useState("12:00");

  const [assignmentModalOpen, setAssignmentModalOpen] = useState(false);
  const [assignmentModalError, setAssignmentModalError] = useState("");
  const [deleteModalAssignment, setDeleteModalAssignment] = useState(null);
  const [deleteModalError, setDeleteModalError] = useState("");

  const slots = useMemo(() => buildHalfHourSlots(), []);

  const openAssignmentModal = useCallback(() => {
    setAssignmentModalError("");
    setConflictBlocks([]);
    setFormRoomId("");
    setFormProfessionalId("");
    setFormWeekday(selectedWeekday);
    setFormStartTime("08:00");
    setFormEndTime("12:00");
    setAssignmentModalOpen(true);
  }, [selectedWeekday]);

  const closeAssignmentModal = useCallback(() => {
    setAssignmentModalOpen(false);
    setAssignmentModalError("");
  }, []);

  const closeDeleteModal = useCallback(() => {
    setDeleteModalAssignment(null);
    setDeleteModalError("");
  }, []);

  useEffect(() => {
    if (!assignmentModalOpen) return;
    const onKey = (e) => {
      if (e.key === "Escape") closeAssignmentModal();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [assignmentModalOpen, closeAssignmentModal]);

  useEffect(() => {
    if (!deleteModalAssignment) return;
    const onKey = (e) => {
      if (e.key === "Escape") closeDeleteModal();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [deleteModalAssignment, closeDeleteModal]);

  const loadCatalogs = useCallback(async () => {
    setError("");
    await Promise.all([
      safeLoad("/locations", setLocations, setError),
      safeLoad("/consulting-rooms", setRooms, setError),
      safeLoad("/professionals", setProfessionals, setError),
    ]);
  }, []);

  useEffect(() => {
    loadCatalogs();
  }, [loadCatalogs]);

  useEffect(() => {
    if (!selectedLocationId && locations.length) {
      setSelectedLocationId(String(locations[0].id));
    }
  }, [locations, selectedLocationId]);

  useEffect(() => {
    const loadRoomHours = async () => {
      if (!rooms.length) {
        setRoomHoursByRoom({});
        return;
      }
      const entries = await Promise.all(
        rooms.map(async (room) => {
          try {
            const list = await apiRequestWithRefresh(`/consulting-rooms/${room.id}/hours`);
            return [room.id, list];
          } catch {
            return [room.id, []];
          }
        })
      );
      setRoomHoursByRoom(Object.fromEntries(entries));
    };
    loadRoomHours();
  }, [rooms]);

  const fetchAssignments = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (selectedLocationId) params.set("location_id", selectedLocationId);
      if (selectedProfessionalId) params.set("professional_id", selectedProfessionalId);
      params.set("weekday", String(selectedWeekday));
      const data = await apiRequestWithRefresh(`/weekly-assignments?${params.toString()}`);
      setAssignments(data);
    } catch (e) {
      setError(e.message || String(e));
      setAssignments([]);
    } finally {
      setLoading(false);
    }
  }, [selectedLocationId, selectedProfessionalId, selectedWeekday]);

  useEffect(() => {
    fetchAssignments();
  }, [fetchAssignments]);

  const visibleRooms = useMemo(
    () =>
      rooms
        .filter((r) => !selectedLocationId || r.location_id === Number(selectedLocationId))
        .slice()
        .sort((a, b) => a.code.localeCompare(b.code)),
    [rooms, selectedLocationId]
  );

  const roomColumnWidth =
    visibleRooms.length > 0
      ? `calc((100% - ${SCHEDULE_COL_WIDTH_PX}px) / ${visibleRooms.length})`
      : "100%";

  const occupancyTableMinWidth = Math.max(640, SCHEDULE_COL_WIDTH_PX + visibleRooms.length * 104);

  const assignmentByRoom = useMemo(() => {
    const map = new Map();
    for (const row of assignments) {
      const list = map.get(row.room_id) || [];
      list.push(row);
      map.set(row.room_id, list);
    }
    return map;
  }, [assignments]);

  const slotCellState = useCallback(
    (roomId, slot) => {
      const dayHours = (roomHoursByRoom[roomId] || []).filter((h) => h.weekday === selectedWeekday);
      const isOpen = dayHours.some((h) => inRange(slot, h.start_time, h.end_time));
      if (!isOpen) return { kind: "closed" };

      const roomAssignments = assignmentByRoom.get(roomId) || [];
      const assignment = roomAssignments.find((a) => inRange(slot, a.start_time, a.end_time));
      if (assignment) {
        const conflict = conflictBlocks.some(
          (c) =>
            c.weekday === selectedWeekday &&
            c.room_id === roomId &&
            inRange(slot, c.start_time, c.end_time)
        );
        return {
          kind: conflict ? "conflict" : "occupied",
          assignment,
        };
      }

      const softConflict = conflictBlocks.some(
        (c) =>
          c.weekday === selectedWeekday &&
          c.room_id === roomId &&
          inRange(slot, c.start_time, c.end_time)
      );
      return { kind: softConflict ? "conflict" : "free" };
    },
    [roomHoursByRoom, selectedWeekday, assignmentByRoom, conflictBlocks]
  );

  const kpis = useMemo(() => {
    let enabled = 0;
    let occupied = 0;
    for (const room of visibleRooms) {
      for (const slot of slots) {
        const state = slotCellState(room.id, slot);
        if (state.kind !== "closed") enabled += 0.5;
        if (state.kind === "occupied" || state.kind === "conflict") occupied += 0.5;
      }
    }
    const rate = enabled > 0 ? (occupied / enabled) * 100 : 0;
    return {
      enabled: Number(enabled.toFixed(2)),
      occupied: Number(occupied.toFixed(2)),
      free: Number(Math.max(0, enabled - occupied).toFixed(2)),
      rate: Number(rate.toFixed(2)),
    };
  }, [visibleRooms, slots, slotCellState]);

  const submitAssignment = async (e) => {
    e.preventDefault();
    setAssignmentModalError("");
    setConflictBlocks([]);
    if (!formProfessionalId) {
      setAssignmentModalError("Elegí un profesional de la lista.");
      return;
    }
    const savedWeekday = Number(formWeekday);
    try {
      await apiRequestWithRefresh("/weekly-assignments", {
        method: "POST",
        body: JSON.stringify({
          room_id: Number(formRoomId),
          professional_id: Number(formProfessionalId),
          weekday: savedWeekday,
          start_time: `${formStartTime}:00`,
          end_time: `${formEndTime}:00`,
        }),
      });
      setAssignmentModalOpen(false);
      setAssignmentModalError("");
      setFormRoomId("");
      setFormProfessionalId("");
      setFormWeekday(savedWeekday);
      setFormStartTime("08:00");
      setFormEndTime("12:00");
      if (savedWeekday !== selectedWeekday) {
        setSelectedWeekday(savedWeekday);
      } else {
        await fetchAssignments();
      }
    } catch (err) {
      const detail = err.detail;
      if (detail && typeof detail === "object" && Array.isArray(detail.conflicts)) {
        setConflictBlocks(detail.conflicts);
      }
      setAssignmentModalError(err.message || String(err));
    }
  };

  const deleteAssignment = async (id) => {
    setError("");
    try {
      await apiRequestWithRefresh(`/weekly-assignments/${id}`, { method: "DELETE" });
      await fetchAssignments();
    } catch (err) {
      setError(err.message || String(err));
    }
  };

  const openDeleteModalFromState = (state) => {
    if (!(state.kind === "occupied" || state.kind === "conflict")) return;
    if (!state.assignment?.id) return;
    setDeleteModalError("");
    setDeleteModalAssignment(state.assignment);
  };

  const confirmDeleteFromModal = async () => {
    if (!deleteModalAssignment?.id) return;
    setDeleteModalError("");
    try {
      await apiRequestWithRefresh(`/weekly-assignments/${deleteModalAssignment.id}`, { method: "DELETE" });
      closeDeleteModal();
      await fetchAssignments();
    } catch (err) {
      setDeleteModalError(err.message || String(err));
    }
  };

  return (
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Ocupación semanal de consultorios</h1>
      <p style={{ ...uiStyles.helpText, marginTop: -6 }}>
        Semana tipo fija. Cerrado = sin horario laboral cargado. Verde = libre habilitado. Azul = ocupado. Rojo = conflicto.
      </p>

      <div style={{ marginBottom: 10 }}>
        <div style={{ marginBottom: 6, fontSize: 13, color: uiTheme.colors.textMuted }}>Ubicación</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {locations.map((loc) => (
            <button
              key={loc.id}
              type="button"
              onClick={() => {
                setSelectedLocationId(String(loc.id));
                setConflictBlocks([]);
              }}
              style={{
                border: `1px solid ${uiTheme.colors.borderStrong}`,
                background: String(loc.id) === selectedLocationId ? uiTheme.colors.primary : "#fff",
                color: String(loc.id) === selectedLocationId ? "#fff" : "#0f172a",
                borderRadius: uiTheme.radius.pill,
                padding: "6px 12px",
                cursor: "pointer",
                fontSize: 13,
                transition: "background-color 140ms ease, color 140ms ease, border-color 140ms ease",
              }}
            >
              {loc.name}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12, alignItems: "flex-end" }}>
        <ProfessionalCombobox
          label="Profesional (filtro visual)"
          professionals={professionals}
          value={selectedProfessionalId}
          onChange={setSelectedProfessionalId}
          showAllEntry
          allEntryLabel="Todos los profesionales (sin filtrar)"
          placeholder="Buscar para filtrar la grilla…"
        />
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12, alignItems: "center" }}>
        {WEEKDAYS.map((d) => (
          <button
            key={d.value}
            type="button"
            onClick={() => {
              setSelectedWeekday(d.value);
              setConflictBlocks([]);
            }}
            style={{
              ...weekdayButtonBaseStyle,
              background: selectedWeekday === d.value ? uiTheme.colors.primary : "#fff",
              color: selectedWeekday === d.value ? "#fff" : uiTheme.colors.text,
              borderColor: selectedWeekday === d.value ? uiTheme.colors.primary : uiTheme.colors.borderStrong,
            }}
          >
            {d.label}
          </button>
        ))}
        <button
          type="button"
          onClick={openAssignmentModal}
          style={{ ...uiStyles.buttonPrimary, marginLeft: 4 }}
        >
          Nueva asignación semanal
        </button>
      </div>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 8, marginBottom: 12 }}>
        <div style={uiStyles.kpiCard}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>% ocupación</div>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{kpis.rate}%</div>
        </div>
        <div style={uiStyles.kpiCard}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Horas habilitadas</div>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{kpis.enabled}</div>
        </div>
        <div style={uiStyles.kpiCard}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Horas ocupadas</div>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{kpis.occupied}</div>
        </div>
        <div style={uiStyles.kpiCard}>
          <div style={{ fontSize: 12, color: uiTheme.colors.textMuted }}>Horas libres</div>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{kpis.free}</div>
        </div>
      </section>

      {error ? <p style={{ color: uiTheme.colors.danger, marginBottom: 12 }}>{String(error)}</p> : null}
      {loading ? <p style={{ color: uiTheme.colors.textMuted, marginBottom: 12 }}>Cargando…</p> : null}

      <div style={{ overflowX: "auto", border: `1px solid ${uiTheme.colors.border}`, borderRadius: uiTheme.radius.md }}>
        <table
          lang="es"
          style={{
            width: "100%",
            minWidth: occupancyTableMinWidth,
            borderCollapse: "collapse",
            tableLayout: "fixed",
            boxSizing: "border-box",
          }}
        >
          <colgroup>
            <col style={{ width: SCHEDULE_COL_WIDTH_PX }} />
            {visibleRooms.map((room) => (
              <col key={room.id} style={{ width: roomColumnWidth }} />
            ))}
          </colgroup>
          <thead>
            <tr style={{ background: "#f8fafc" }}>
              <th
                style={{
                  borderBottom: `1px solid ${uiTheme.colors.border}`,
                  padding: "8px 6px",
                  textAlign: "left",
                  position: "sticky",
                  left: 0,
                  background: "#f8fafc",
                  zIndex: 2,
                  width: SCHEDULE_COL_WIDTH_PX,
                  maxWidth: SCHEDULE_COL_WIDTH_PX,
                  boxSizing: "border-box",
                  fontSize: 11,
                  boxShadow: "4px 0 10px -6px rgba(15, 43, 39, 0.12)",
                }}
              >
                Horario
              </th>
              {visibleRooms.map((room) => (
                <th
                  key={room.id}
                  style={{
                    borderBottom: `1px solid ${uiTheme.colors.border}`,
                    padding: 6,
                    fontSize: 11,
                    width: roomColumnWidth,
                    minWidth: 96,
                    boxSizing: "border-box",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                  title={room.code}
                >
                  {room.code}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slots.map((slot) => (
              <tr key={slot.key}>
                <td
                  style={{
                    borderBottom: `1px solid ${uiTheme.colors.border}`,
                    padding: "6px 6px",
                    whiteSpace: "nowrap",
                    position: "sticky",
                    left: 0,
                    background: "#fff",
                    fontSize: 11,
                    fontWeight: 600,
                    width: SCHEDULE_COL_WIDTH_PX,
                    maxWidth: SCHEDULE_COL_WIDTH_PX,
                    boxSizing: "border-box",
                    boxShadow: "4px 0 10px -6px rgba(15, 43, 39, 0.12)",
                    zIndex: 1,
                  }}
                >
                  {slot.key}
                </td>
                {visibleRooms.map((room) => {
                  const state = slotCellState(room.id, slot);
                  let bg = "#e2e8f0";
                  let text = "";
                  if (state.kind === "free") bg = "#dcfce7";
                  if (state.kind === "occupied") bg = "#dbeafe";
                  if (state.kind === "conflict") bg = "#fecaca";
                  if (state.kind === "occupied" || state.kind === "conflict") {
                    text = state.assignment?.professional_full_name || "";
                  }
                  return (
                    <td
                      key={`${slot.key}-${room.id}`}
                      title={text || undefined}
                      onClick={() => openDeleteModalFromState(state)}
                      style={{
                        borderBottom: `1px solid ${uiTheme.colors.border}`,
                        borderLeft: "1px solid #edf4f2",
                        padding: "4px 4px",
                        fontSize: 10,
                        width: roomColumnWidth,
                        minWidth: 96,
                        boxSizing: "border-box",
                        background: bg,
                        textAlign: "center",
                        verticalAlign: "middle",
                        lineHeight: 1.25,
                        cursor: state.kind === "occupied" || state.kind === "conflict" ? "pointer" : "default",
                      }}
                    >
                      {text ? <span style={slotCellNameStyle}>{text}</span> : null}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 12 }}>
        <h2 style={{ fontSize: "1rem", marginBottom: 6 }}>Asignaciones del día</h2>
        <ul style={uiStyles.listCard}>
          {assignments.map((a) => (
            <li
              key={a.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: 8,
                padding: "8px 10px",
                borderBottom: `1px solid ${uiTheme.colors.border}`,
              }}
            >
              <span>
                {a.room_code} · {a.start_time}–{a.end_time} · <strong>{a.professional_full_name}</strong>
              </span>
              <button type="button" onClick={() => deleteAssignment(a.id)} style={uiStyles.buttonDanger}>
                eliminar
              </button>
            </li>
          ))}
          {assignments.length === 0 ? <li style={{ padding: "10px 12px", color: uiTheme.colors.textMuted }}>Sin asignaciones</li> : null}
        </ul>
      </div>

      {assignmentModalOpen ? (
        <div
          role="presentation"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1000,
            background: "rgba(15, 23, 42, 0.45)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            padding: "max(16px, 4vh) 16px",
            overflowY: "auto",
          }}
          onClick={closeAssignmentModal}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="assignment-modal-title"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: uiTheme.radius.md,
              maxWidth: 560,
              width: "100%",
              marginTop: 0,
              marginBottom: 24,
              padding: 22,
              boxShadow: "0 25px 50px rgba(15, 23, 42, 0.18)",
              border: `1px solid ${uiTheme.colors.border}`,
            }}
          >
            <h2 id="assignment-modal-title" style={{ marginTop: 0, marginBottom: 12, fontSize: "1.15rem" }}>
              Nueva asignación semanal
            </h2>
            {assignmentModalError ? (
              <p style={{ color: uiTheme.colors.danger, marginTop: 0, marginBottom: 14, fontSize: 14 }}>{assignmentModalError}</p>
            ) : null}
            <form
              onSubmit={submitAssignment}
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "10px 12px",
                alignItems: "flex-end",
              }}
            >
              <label style={formFieldLabelStyle}>
                Consultorio
                <select
                  value={formRoomId}
                  onChange={(e) => setFormRoomId(e.target.value)}
                  required
                  style={{ ...alignedNativeFormControlStyle, minWidth: 120 }}
                >
                  <option value="">Elegir…</option>
                  {visibleRooms.map((r) => (
                    <option key={r.id} value={r.id}>
                      #{r.id} {r.code}
                    </option>
                  ))}
                </select>
              </label>
              <ProfessionalCombobox
                label="Profesional"
                professionals={professionals}
                value={formProfessionalId}
                onChange={setFormProfessionalId}
                required
                placeholder="Buscar por nombre, DNI o matrícula…"
              />
              <label style={formFieldLabelStyle}>
                Día
                <select
                  value={formWeekday}
                  onChange={(e) => setFormWeekday(Number(e.target.value))}
                  style={{ ...alignedNativeFormControlStyle, minWidth: 112 }}
                >
                  {WEEKDAYS.map((d) => (
                    <option key={d.value} value={d.value}>
                      {d.label}
                    </option>
                  ))}
                </select>
              </label>
              <label style={formFieldLabelStyle}>
                Desde
                <input
                  type="time"
                  step={1800}
                  value={formStartTime}
                  onChange={(e) => setFormStartTime(e.target.value)}
                  required
                  style={{ ...alignedNativeFormControlStyle, minWidth: 104 }}
                />
              </label>
              <label style={formFieldLabelStyle}>
                Hasta
                <input
                  type="time"
                  step={1800}
                  value={formEndTime}
                  onChange={(e) => setFormEndTime(e.target.value)}
                  required
                  style={{ ...alignedNativeFormControlStyle, minWidth: 104 }}
                />
              </label>
              <div style={{ flexBasis: "100%", display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8, justifyContent: "flex-end" }}>
                <button
                  type="button"
                  onClick={closeAssignmentModal}
                  style={{ ...alignedNativeFormControlStyle, ...uiStyles.buttonSecondary, padding: "6px 16px" }}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  style={{ ...alignedNativeFormControlStyle, ...uiStyles.buttonPrimary, padding: "6px 16px" }}
                >
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}

      {deleteModalAssignment ? (
        <div
          role="presentation"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1000,
            background: "rgba(15, 23, 42, 0.45)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            padding: "max(16px, 4vh) 16px",
            overflowY: "auto",
          }}
          onClick={closeDeleteModal}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-assignment-modal-title"
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: uiTheme.radius.md,
              maxWidth: 520,
              width: "100%",
              marginBottom: 24,
              padding: 22,
              boxShadow: "0 25px 50px rgba(15, 23, 42, 0.18)",
              border: `1px solid ${uiTheme.colors.border}`,
            }}
          >
            <h2 id="delete-assignment-modal-title" style={{ marginTop: 0, marginBottom: 10, fontSize: "1.1rem" }}>
              Eliminar asignación semanal
            </h2>
            <p style={{ marginTop: 0, marginBottom: 10, color: uiTheme.colors.textMuted }}>
              Esta acción elimina el bloque completo de la semana tipo.
            </p>
            <div style={{ ...uiStyles.kpiCard, marginBottom: 12, lineHeight: 1.4 }}>
              <div>
                <strong>Profesional:</strong> {deleteModalAssignment.professional_full_name}
              </div>
              <div>
                <strong>Consultorio:</strong> {deleteModalAssignment.room_code}
              </div>
              <div>
                <strong>Día:</strong> {WEEKDAYS.find((d) => d.value === selectedWeekday)?.label || selectedWeekday}
              </div>
              <div>
                <strong>Horario:</strong> {deleteModalAssignment.start_time}–{deleteModalAssignment.end_time}
              </div>
            </div>
            {deleteModalError ? <p style={{ color: uiTheme.colors.danger, margin: "0 0 10px" }}>{deleteModalError}</p> : null}
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button type="button" onClick={closeDeleteModal} style={uiStyles.buttonSecondary}>
                Cancelar
              </button>
              <button type="button" onClick={confirmDeleteFromModal} style={uiStyles.buttonDanger}>
                Eliminar bloque
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
