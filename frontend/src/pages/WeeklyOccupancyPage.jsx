import { useCallback, useEffect, useMemo, useState } from "react";

import { ProfessionalCombobox, alignedNativeFormControlStyle } from "../components/ProfessionalCombobox";
import { safeLoad } from "../lib/apiHelpers";
import { apiRequestWithRefresh } from "../services/api";

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
  color: "#334155",
};

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

  const slots = useMemo(() => buildHalfHourSlots(), []);

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
    setError("");
    setConflictBlocks([]);
    if (!formProfessionalId) {
      setError("Elegí un profesional de la lista.");
      return;
    }
    try {
      await apiRequestWithRefresh("/weekly-assignments", {
        method: "POST",
        body: JSON.stringify({
          room_id: Number(formRoomId),
          professional_id: Number(formProfessionalId),
          weekday: Number(formWeekday),
          start_time: `${formStartTime}:00`,
          end_time: `${formEndTime}:00`,
        }),
      });
      if (Number(formWeekday) !== selectedWeekday) {
        setSelectedWeekday(Number(formWeekday));
      } else {
        await fetchAssignments();
      }
    } catch (err) {
      const detail = err.detail;
      if (detail && typeof detail === "object" && Array.isArray(detail.conflicts)) {
        setConflictBlocks(detail.conflicts);
      }
      setError(err.message || String(err));
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

  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Ocupación semanal de consultorios</h1>
      <p style={{ color: "#64748b", marginTop: -6 }}>
        Semana tipo fija. Cerrado = sin horario laboral cargado. Verde = libre habilitado. Azul = ocupado. Rojo = conflicto.
      </p>

      <div style={{ marginBottom: 10 }}>
        <div style={{ marginBottom: 6, fontSize: 13, color: "#64748b" }}>Ubicación</div>
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
                border: "1px solid #cbd5e1",
                background: String(loc.id) === selectedLocationId ? "#0f766e" : "#fff",
                color: String(loc.id) === selectedLocationId ? "#fff" : "#0f172a",
                borderRadius: 999,
                padding: "6px 12px",
                cursor: "pointer",
                fontSize: 13,
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

      <form
        onSubmit={submitAssignment}
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "10px 12px",
          alignItems: "flex-end",
          border: "1px solid #e2e8f0",
          borderRadius: 8,
          padding: 12,
          marginBottom: 12,
          background: "#f8fafc",
        }}
      >
        <strong style={{ flexBasis: "100%", marginBottom: 2 }}>Nueva asignación semanal</strong>
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
        <button
          type="submit"
          style={{
            ...alignedNativeFormControlStyle,
            cursor: "pointer",
            fontWeight: 600,
            backgroundColor: "#e2e8f0",
            borderColor: "#94a3b8",
            color: "#0f172a",
            padding: "6px 16px",
          }}
        >
          Guardar
        </button>
      </form>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
        {WEEKDAYS.map((d) => (
          <button
            key={d.value}
            type="button"
            onClick={() => {
              setSelectedWeekday(d.value);
              setConflictBlocks([]);
            }}
            style={{
              border: "1px solid #cbd5e1",
              background: selectedWeekday === d.value ? "#0f766e" : "#fff",
              color: selectedWeekday === d.value ? "#fff" : "#0f172a",
              borderRadius: 6,
              padding: "6px 10px",
              cursor: "pointer",
            }}
          >
            {d.label}
          </button>
        ))}
      </div>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 8, marginBottom: 12 }}>
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 10 }}>
          <div style={{ fontSize: 12, color: "#64748b" }}>% ocupación</div>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{kpis.rate}%</div>
        </div>
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 10 }}>
          <div style={{ fontSize: 12, color: "#64748b" }}>Horas habilitadas</div>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{kpis.enabled}</div>
        </div>
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 10 }}>
          <div style={{ fontSize: 12, color: "#64748b" }}>Horas ocupadas</div>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{kpis.occupied}</div>
        </div>
        <div style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 10 }}>
          <div style={{ fontSize: 12, color: "#64748b" }}>Horas libres</div>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{kpis.free}</div>
        </div>
      </section>

      {error ? <p style={{ color: "crimson", marginBottom: 12 }}>{String(error)}</p> : null}
      {loading ? <p style={{ color: "#475569", marginBottom: 12 }}>Cargando…</p> : null}

      <div style={{ overflowX: "auto", border: "1px solid #e2e8f0", borderRadius: 8 }}>
        <table lang="es" style={{ width: "100%", borderCollapse: "collapse", minWidth: 1100 }}>
          <thead>
            <tr style={{ background: "#f8fafc" }}>
              <th style={{ borderBottom: "1px solid #e2e8f0", padding: 8, textAlign: "left", position: "sticky", left: 0, background: "#f8fafc" }}>
                Consultorio
              </th>
              {slots.map((slot) => (
                <th key={slot.key} style={{ borderBottom: "1px solid #e2e8f0", padding: 6, fontSize: 11 }}>
                  {slot.key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRooms.map((room) => (
              <tr key={room.id}>
                <td
                  style={{
                    borderBottom: "1px solid #f1f5f9",
                    padding: 8,
                    whiteSpace: "nowrap",
                    position: "sticky",
                    left: 0,
                    background: "#fff",
                  }}
                >
                  <strong>{room.code}</strong>
                </td>
                {slots.map((slot) => {
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
                      key={`${room.id}-${slot.key}`}
                      title={text || undefined}
                      style={{
                        borderBottom: "1px solid #f1f5f9",
                        borderLeft: "1px solid #f8fafc",
                        padding: "4px 3px",
                        fontSize: 10,
                        minWidth: 78,
                        maxWidth: 78,
                        width: 78,
                        background: bg,
                        textAlign: "center",
                        verticalAlign: "middle",
                        lineHeight: 1.25,
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
        <ul style={{ paddingLeft: 18 }}>
          {assignments.map((a) => (
            <li key={a.id} style={{ marginBottom: 6 }}>
              {a.room_code} · {a.start_time}–{a.end_time} · <strong>{a.professional_full_name}</strong>{" "}
              <button type="button" onClick={() => deleteAssignment(a.id)}>
                eliminar
              </button>
            </li>
          ))}
          {assignments.length === 0 ? <li>Sin asignaciones</li> : null}
        </ul>
      </div>
    </section>
  );
}
