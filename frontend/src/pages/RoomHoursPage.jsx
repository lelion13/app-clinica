import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";

const WEEKDAYS = [
  ["0", "Domingo"],
  ["1", "Lunes"],
  ["2", "Martes"],
  ["3", "Miércoles"],
  ["4", "Jueves"],
  ["5", "Viernes"],
  ["6", "Sábado"],
];

export function RoomHoursPage() {
  const [error, setError] = useState("");
  const [rooms, setRooms] = useState([]);
  const [roomHours, setRoomHours] = useState([]);
  const [hourRoomId, setHourRoomId] = useState("");
  const [hourWeekday, setHourWeekday] = useState("0");
  const [hourStart, setHourStart] = useState("08:00");
  const [hourEnd, setHourEnd] = useState("12:00");

  const loadRooms = async () => {
    setError("");
    await safeLoad("/consulting-rooms", setRooms, setError);
  };

  useEffect(() => {
    loadRooms();
  }, []);

  useEffect(() => {
    if (!hourRoomId) {
      setRoomHours([]);
      return;
    }
    safeLoad(`/consulting-rooms/${hourRoomId}/hours`, setRoomHours, setError);
  }, [hourRoomId]);

  const submitHour = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/consulting-rooms/hours", {
      method: "POST",
      body: JSON.stringify({
        room_id: Number(hourRoomId),
        weekday: Number(hourWeekday),
        start_time: hourStart,
        end_time: hourEnd,
      }),
    });
    await safeLoad(`/consulting-rooms/${hourRoomId}/hours`, setRoomHours, setError);
  };

  const removeHour = async (hourId) => {
    await apiRequestWithRefresh(`/consulting-rooms/hours/${hourId}`, { method: "DELETE" });
    if (hourRoomId) {
      await safeLoad(`/consulting-rooms/${hourRoomId}/hours`, setRoomHours, setError);
    }
  };

  const weekdayLabel = (n) => WEEKDAYS.find(([v]) => v === String(n))?.[1] ?? n;

  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Horarios de consultorio</h1>
      <p style={{ color: "#64748b" }}>
        Franjas habilitadas por día de la semana (misma convención que el calendario: 0 = domingo … 6 = sábado).
      </p>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      <form onSubmit={submitHour} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16, alignItems: "flex-end" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Consultorio
          <select value={hourRoomId} onChange={(event) => setHourRoomId(event.target.value)} required>
            <option value="">Elegir…</option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>
                #{room.id} - {room.code}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Día
          <select value={hourWeekday} onChange={(event) => setHourWeekday(event.target.value)}>
            {WEEKDAYS.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Desde
          <input type="time" value={hourStart} onChange={(event) => setHourStart(event.target.value)} required />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Hasta
          <input type="time" value={hourEnd} onChange={(event) => setHourEnd(event.target.value)} required />
        </label>
        <button type="submit">Agregar franja</button>
      </form>
      <ul style={{ paddingLeft: 20 }}>
        {roomHours.map((hour) => (
          <li key={hour.id} style={{ marginBottom: 8 }}>
            #{hour.id} — {weekdayLabel(hour.weekday)} — {hour.start_time} a {hour.end_time}{" "}
            <button type="button" onClick={() => removeHour(hour.id)}>
              eliminar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
