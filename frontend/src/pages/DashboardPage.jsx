import { useEffect, useMemo, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import esLocale from "@fullcalendar/core/locales/es";
import { Link } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { apiRequestWithRefresh } from "../services/api";

async function safeLoad(path, setData, setError) {
  try {
    const data = await apiRequestWithRefresh(path);
    setData(data);
  } catch (err) {
    setError(err.message);
  }
}

export function DashboardPage() {
  const { user, isAdmin, logout } = useAuth();
  const [error, setError] = useState("");
  const [locations, setLocations] = useState([]);
  const [professionals, setProfessionals] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [roomHours, setRoomHours] = useState([]);
  const [users, setUsers] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [calendarRange, setCalendarRange] = useState({ start: null, end: null });

  const [locationName, setLocationName] = useState("");
  const [professionalName, setProfessionalName] = useState("");
  const [professionalLicense, setProfessionalLicense] = useState("");
  const [roomLocationId, setRoomLocationId] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [hourRoomId, setHourRoomId] = useState("");
  const [hourWeekday, setHourWeekday] = useState("0");
  const [hourStart, setHourStart] = useState("08:00");
  const [hourEnd, setHourEnd] = useState("12:00");
  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserPassword, setNewUserPassword] = useState("");
  const [newUserRole, setNewUserRole] = useState("operador");
  const [bookingRoomId, setBookingRoomId] = useState("");
  const [bookingProfessionalId, setBookingProfessionalId] = useState("");
  const [bookingStartAt, setBookingStartAt] = useState("");
  const [bookingEndAt, setBookingEndAt] = useState("");

  const loadAll = async () => {
    setError("");
    await Promise.all([
      safeLoad("/locations", setLocations, setError),
      safeLoad("/professionals", setProfessionals, setError),
      safeLoad("/consulting-rooms", setRooms, setError),
      isAdmin ? safeLoad("/users", setUsers, setError) : Promise.resolve(),
    ]);
    if (calendarRange.start && calendarRange.end) {
      await safeLoad(
        `/bookings?start_at=${encodeURIComponent(calendarRange.start)}&end_at=${encodeURIComponent(calendarRange.end)}`,
        setBookings,
        setError
      );
    }
  };

  useEffect(() => {
    loadAll();
  }, [isAdmin]);

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

  useEffect(() => {
    if (!hourRoomId) {
      setRoomHours([]);
      return;
    }
    safeLoad(`/consulting-rooms/${hourRoomId}/hours`, setRoomHours, setError);
  }, [hourRoomId]);

  const submitLocation = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/locations", {
      method: "POST",
      body: JSON.stringify({ name: locationName }),
    });
    setLocationName("");
    await loadAll();
  };

  const submitProfessional = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/professionals", {
      method: "POST",
      body: JSON.stringify({ full_name: professionalName, license_number: professionalLicense || null }),
    });
    setProfessionalName("");
    setProfessionalLicense("");
    await loadAll();
  };

  const submitRoom = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/consulting-rooms", {
      method: "POST",
      body: JSON.stringify({ location_id: Number(roomLocationId), code: roomCode }),
    });
    setRoomCode("");
    await loadAll();
  };

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

  const submitUser = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/users", {
      method: "POST",
      body: JSON.stringify({
        name: newUserName,
        email: newUserEmail,
        password: newUserPassword,
        role: newUserRole,
        is_active: true,
      }),
    });
    setNewUserName("");
    setNewUserEmail("");
    setNewUserPassword("");
    setNewUserRole("operador");
    await loadAll();
  };

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
    await loadAll();
  };

  const removeItem = async (path) => {
    await apiRequestWithRefresh(path, { method: "DELETE" });
    await loadAll();
  };

  const doLogout = async () => {
    await logout();
    window.location.href = "/login";
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
    const shouldDelete = window.confirm("Eliminar reserva seleccionada?");
    if (!shouldDelete) return;
    await apiRequestWithRefresh(`/bookings/${bookingId}`, { method: "DELETE" });
    await loadAll();
  };

  return (
    <main style={{ maxWidth: 1000, margin: "24px auto", display: "grid", gap: 20 }}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div>
          <h1>Panel de gestion</h1>
          <p>
            Sesion: {user?.name} ({user?.role})
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <Link to="/setup">Setup</Link>
          <button type="button" onClick={doLogout}>
            Cerrar sesion
          </button>
        </div>
      </header>

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

      <section style={{ border: "1px solid #ddd", padding: 12 }}>
        <h2>Agenda (dia/semana)</h2>
        <form onSubmit={submitBooking} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
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
          <input
            type="datetime-local"
            value={bookingStartAt}
            onChange={(event) => setBookingStartAt(event.target.value)}
            required
          />
          <input
            type="datetime-local"
            value={bookingEndAt}
            onChange={(event) => setBookingEndAt(event.target.value)}
            required
          />
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

      <section style={{ border: "1px solid #ddd", padding: 12 }}>
        <h2>Ubicaciones</h2>
        <form onSubmit={submitLocation} style={{ display: "flex", gap: 8 }}>
          <input value={locationName} onChange={(event) => setLocationName(event.target.value)} placeholder="Nombre" required />
          <button type="submit">Agregar</button>
        </form>
        <ul>
          {locations.map((item) => (
            <li key={item.id}>
              #{item.id} - {item.name}{" "}
              <button type="button" onClick={() => removeItem(`/locations/${item.id}`)}>
                eliminar
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section style={{ border: "1px solid #ddd", padding: 12 }}>
        <h2>Profesionales</h2>
        <form onSubmit={submitProfessional} style={{ display: "flex", gap: 8 }}>
          <input
            value={professionalName}
            onChange={(event) => setProfessionalName(event.target.value)}
            placeholder="Nombre completo"
            required
          />
          <input
            value={professionalLicense}
            onChange={(event) => setProfessionalLicense(event.target.value)}
            placeholder="Matricula"
          />
          <button type="submit">Agregar</button>
        </form>
        <ul>
          {professionals.map((item) => (
            <li key={item.id}>
              #{item.id} - {item.full_name} ({item.license_number || "sin matricula"}){" "}
              <button type="button" onClick={() => removeItem(`/professionals/${item.id}`)}>
                eliminar
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section style={{ border: "1px solid #ddd", padding: 12 }}>
        <h2>Consultorios</h2>
        <form onSubmit={submitRoom} style={{ display: "flex", gap: 8 }}>
          <select value={roomLocationId} onChange={(event) => setRoomLocationId(event.target.value)} required>
            <option value="">Ubicacion</option>
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                #{location.id} - {location.name}
              </option>
            ))}
          </select>
          <input value={roomCode} onChange={(event) => setRoomCode(event.target.value)} placeholder="Codigo" required />
          <button type="submit">Agregar</button>
        </form>
        <ul>
          {rooms.map((item) => (
            <li key={item.id}>
              #{item.id} - Loc {item.location_id} - {item.code}{" "}
              <button type="button" onClick={() => removeItem(`/consulting-rooms/${item.id}`)}>
                eliminar
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section style={{ border: "1px solid #ddd", padding: 12 }}>
        <h2>Horarios operativos de consultorio</h2>
        <form onSubmit={submitHour} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <select value={hourRoomId} onChange={(event) => setHourRoomId(event.target.value)} required>
            <option value="">Consultorio</option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>
                #{room.id} - {room.code}
              </option>
            ))}
          </select>
          <select value={hourWeekday} onChange={(event) => setHourWeekday(event.target.value)}>
            <option value="0">Domingo</option>
            <option value="1">Lunes</option>
            <option value="2">Martes</option>
            <option value="3">Miercoles</option>
            <option value="4">Jueves</option>
            <option value="5">Viernes</option>
            <option value="6">Sabado</option>
          </select>
          <input type="time" value={hourStart} onChange={(event) => setHourStart(event.target.value)} required />
          <input type="time" value={hourEnd} onChange={(event) => setHourEnd(event.target.value)} required />
          <button type="submit">Agregar</button>
        </form>
        <ul>
          {roomHours.map((hour) => (
            <li key={hour.id}>
              #{hour.id} - dia {hour.weekday} - {hour.start_time} a {hour.end_time}{" "}
              <button type="button" onClick={() => removeItem(`/consulting-rooms/hours/${hour.id}`)}>
                eliminar
              </button>
            </li>
          ))}
        </ul>
      </section>

      {isAdmin ? (
        <section style={{ border: "1px solid #ddd", padding: 12 }}>
          <h2>Usuarios (solo admin)</h2>
          <form onSubmit={submitUser} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <input value={newUserName} onChange={(event) => setNewUserName(event.target.value)} placeholder="Nombre" required />
            <input
              type="email"
              value={newUserEmail}
              onChange={(event) => setNewUserEmail(event.target.value)}
              placeholder="Email"
              required
            />
            <input
              type="password"
              value={newUserPassword}
              onChange={(event) => setNewUserPassword(event.target.value)}
              placeholder="Contrasena"
              required
            />
            <select value={newUserRole} onChange={(event) => setNewUserRole(event.target.value)}>
              <option value="operador">operador</option>
              <option value="admin">admin</option>
            </select>
            <button type="submit">Crear usuario</button>
          </form>
          <ul>
            {users.map((item) => (
              <li key={item.id}>
                #{item.id} - {item.name} - {item.email} ({item.role}){" "}
                <button type="button" onClick={() => removeItem(`/users/${item.id}`)}>
                  eliminar
                </button>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </main>
  );
}
