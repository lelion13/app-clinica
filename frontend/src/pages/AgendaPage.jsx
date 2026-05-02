import { useEffect, useMemo, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import esLocale from "@fullcalendar/core/locales/es";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";

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

  const submitBooking = async (event) => {
    event.preventDefault();
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

  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Agenda</h1>
      <p style={{ color: "#64748b", marginTop: -4 }}>
        Reservas por consultorio y profesional. Podés arrastrar en el calendario para prefijar horario o completar el formulario.
      </p>

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

      <form onSubmit={submitBooking} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16, alignItems: "flex-end" }}>
        <select value={bookingRoomId} onChange={(event) => setBookingRoomId(event.target.value)} required>
          <option value="">Consultorio</option>
          {rooms.map((room) => (
            <option key={room.id} value={room.id}>
              #{room.id} - {room.code}
            </option>
          ))}
        </select>
        <select
          value={bookingProfessionalId}
          onChange={(event) => setBookingProfessionalId(event.target.value)}
          required
        >
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
        <button type="submit">Crear reserva</button>
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
