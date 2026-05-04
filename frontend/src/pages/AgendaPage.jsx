import { useEffect, useMemo, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import esLocale from "@fullcalendar/core/locales/es";

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

function isoDate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function AgendaPage() {
  const [error, setError] = useState("");
  const [professionals, setProfessionals] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [calendarRange, setCalendarRange] = useState({ start: null, end: null });

  const [bookingRoomId, setBookingRoomId] = useState("");
  const [bookingProfessionalId, setBookingProfessionalId] = useState("");
  const [bookingStartAt, setBookingStartAt] = useState("");
  const [bookingEndAt, setBookingEndAt] = useState("");

  const [recurringWeekday, setRecurringWeekday] = useState("1");
  const [recurringStartTime, setRecurringStartTime] = useState("09:00");
  const [recurringEndTime, setRecurringEndTime] = useState("12:00");
  const [periodStart, setPeriodStart] = useState(() => isoDate(new Date()));
  const [periodEnd, setPeriodEnd] = useState(() => {
    const d = new Date();
    d.setMonth(d.getMonth() + 3);
    return isoDate(d);
  });

  const loadCatalog = async () => {
    setError("");
    await Promise.all([safeLoad("/professionals", setProfessionals, setError), safeLoad("/consulting-rooms", setRooms, setError)]);
  };

  const loadBookingsForRange = async (range) => {
    if (!range?.start || !range?.end) return;
    await safeLoad(
      `/bookings?start_at=${encodeURIComponent(range.start)}&end_at=${encodeURIComponent(range.end)}`,
      setBookings,
      setError
    );
  };

  useEffect(() => {
    loadCatalog();
  }, []);

  const calendarEvents = useMemo(
    () =>
      bookings.map((booking) => {
        const room = rooms.find((item) => item.id === booking.room_id);
        const professional = professionals.find((item) => item.id === booking.professional_id);
        return {
          id: String(booking.id),
          title: `${room?.code || "Consultorio"} - ${professional?.full_name || "Profesional"}`,
          start: booking.start_at,
          end: booking.end_at,
          extendedProps: booking,
        };
      }),
    [bookings, rooms, professionals]
  );

  const fmtTimeForApi = (hm) => (hm && hm.length === 5 ? `${hm}:00` : hm);

  const submitRecurring = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await apiRequestWithRefresh("/bookings/recurring", {
        method: "POST",
        body: JSON.stringify({
          room_id: Number(bookingRoomId),
          professional_id: Number(bookingProfessionalId),
          weekday: Number(recurringWeekday),
          start_time: fmtTimeForApi(recurringStartTime),
          end_time: fmtTimeForApi(recurringEndTime),
          period_start: periodStart,
          period_end: periodEnd,
        }),
      });
      await loadCatalog();
      await loadBookingsForRange(calendarRange);
    } catch (e) {
      setError(e.message || String(e));
    }
  };

  const submitBooking = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await apiRequestWithRefresh("/bookings", {
        method: "POST",
        body: JSON.stringify({
          room_id: Number(bookingRoomId),
          professional_id: Number(bookingProfessionalId),
          start_at: new Date(bookingStartAt).toISOString(),
          end_at: new Date(bookingEndAt).toISOString(),
        }),
      });
      setBookingStartAt("");
      setBookingEndAt("");
      await loadCatalog();
      await loadBookingsForRange(calendarRange);
    } catch (e) {
      setError(e.message || String(e));
    }
  };

  const removeBooking = async (bookingId) => {
    await apiRequestWithRefresh(`/bookings/${bookingId}`, { method: "DELETE" });
    await loadBookingsForRange(calendarRange);
  };

  const onCalendarSelect = (selection) => {
    setBookingStartAt(selection.startStr.slice(0, 16));
    setBookingEndAt(selection.endStr.slice(0, 16));
  };

  const onCalendarDatesSet = async (info) => {
    const nextRange = { start: info.start.toISOString(), end: info.end.toISOString() };
    setCalendarRange(nextRange);
    await safeLoad(
      `/bookings?start_at=${encodeURIComponent(nextRange.start)}&end_at=${encodeURIComponent(nextRange.end)}`,
      setBookings,
      setError
    );
  };

  const onCalendarEventClick = async (clickInfo) => {
    const bookingId = clickInfo.event.id;
    const shouldDelete = window.confirm("¿Eliminar esta reserva?");
    if (!shouldDelete) return;
    await removeBooking(bookingId);
  };

  const sharedRoomProfFields = (
    <>
      <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
        Consultorio
        <select value={bookingRoomId} onChange={(event) => setBookingRoomId(event.target.value)} required>
          <option value="">Elegir…</option>
          {rooms.map((room) => (
            <option key={room.id} value={room.id}>
              #{room.id} - {room.code}
            </option>
          ))}
        </select>
      </label>
      <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
        Profesional
        <select value={bookingProfessionalId} onChange={(event) => setBookingProfessionalId(event.target.value)} required>
          <option value="">Elegir…</option>
          {professionals.map((item) => (
            <option key={item.id} value={item.id}>
              #{item.id} - {item.full_name}
            </option>
          ))}
        </select>
      </label>
    </>
  );

  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Agenda</h1>
      <p style={{ color: "#64748b", marginTop: -4 }}>
        El modelo habitual es un <strong>turno fijo semanal</strong> (mismo día y horario que definís en{" "}
        <em>Horarios de consultorio</em>): elegís el día de la semana, la franja horaria y el rango de fechas; el sistema
        crea una reserva por cada ocurrencia. Para una sola fecha podés usar el bloque de abajo o arrastrar en el
        calendario.
      </p>

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

      <form
        onSubmit={submitRecurring}
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 12,
          marginBottom: 20,
          alignItems: "flex-end",
          padding: 12,
          border: "1px solid #e2e8f0",
          borderRadius: 8,
          background: "#f8fafc",
        }}
      >
        <div style={{ flexBasis: "100%", fontWeight: 600, fontSize: "0.95rem" }}>Turno fijo semanal</div>
        {sharedRoomProfFields}
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Día de la semana
          <select value={recurringWeekday} onChange={(event) => setRecurringWeekday(event.target.value)} required>
            {WEEKDAYS.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Desde (hora)
          <input type="time" value={recurringStartTime} onChange={(event) => setRecurringStartTime(event.target.value)} required />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Hasta (hora)
          <input type="time" value={recurringEndTime} onChange={(event) => setRecurringEndTime(event.target.value)} required />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Período desde
          <input type="date" value={periodStart} onChange={(event) => setPeriodStart(event.target.value)} required />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: "0.85rem" }}>
          Período hasta
          <input type="date" value={periodEnd} onChange={(event) => setPeriodEnd(event.target.value)} required />
        </label>
        <button type="submit">Crear turnos en el período</button>
      </form>

      <form
        onSubmit={submitBooking}
        style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16, alignItems: "flex-end" }}
      >
        <div style={{ flexBasis: "100%", fontSize: "0.9rem", color: "#64748b" }}>
          Reserva puntual (una sola fecha y hora)
        </div>
        <select value={bookingRoomId} onChange={(event) => setBookingRoomId(event.target.value)} required>
          <option value="">Consultorio</option>
          {rooms.map((room) => (
            <option key={room.id} value={room.id}>
              #{room.id} - {room.code}
            </option>
          ))}
        </select>
        <select value={bookingProfessionalId} onChange={(event) => setBookingProfessionalId(event.target.value)} required>
          <option value="">Profesional</option>
          {professionals.map((item) => (
            <option key={item.id} value={item.id}>
              #{item.id} - {item.full_name}
            </option>
          ))}
        </select>
        <label style={{ display: "flex", flexDirection: "column", fontSize: "0.8rem", gap: 4 }}>
          Inicio
          <input
            type="datetime-local"
            value={bookingStartAt}
            onChange={(event) => setBookingStartAt(event.target.value)}
            required
          />
        </label>
        <label style={{ display: "flex", flexDirection: "column", fontSize: "0.8rem", gap: 4 }}>
          Fin
          <input
            type="datetime-local"
            value={bookingEndAt}
            onChange={(event) => setBookingEndAt(event.target.value)}
            required
          />
        </label>
        <button type="submit">Crear una reserva</button>
      </form>

      <FullCalendar
        plugins={[timeGridPlugin, dayGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: "prev,next today",
          center: "title",
          right: "timeGridDay,timeGridWeek,dayGridMonth",
        }}
        selectable
        selectMirror
        select={onCalendarSelect}
        datesSet={onCalendarDatesSet}
        events={calendarEvents}
        eventClick={onCalendarEventClick}
        height={650}
        locale={esLocale}
        allDaySlot={false}
        slotMinTime="06:00:00"
        slotMaxTime="22:00:00"
      />
    </section>
  );
}
