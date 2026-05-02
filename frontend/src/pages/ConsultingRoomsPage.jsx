import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";

export function ConsultingRoomsPage() {
  const [error, setError] = useState("");
  const [locations, setLocations] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [roomLocationId, setRoomLocationId] = useState("");
  const [roomCode, setRoomCode] = useState("");

  const load = async () => {
    setError("");
    await Promise.all([safeLoad("/locations", setLocations, setError), safeLoad("/consulting-rooms", setRooms, setError)]);
  };

  useEffect(() => {
    load();
  }, []);

  const submitRoom = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/consulting-rooms", {
      method: "POST",
      body: JSON.stringify({ location_id: Number(roomLocationId), code: roomCode }),
    });
    setRoomCode("");
    await load();
  };

  const removeItem = async (id) => {
    await apiRequestWithRefresh(`/consulting-rooms/${id}`, { method: "DELETE" });
    await load();
  };

  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Consultorios</h1>
      <p style={{ color: "#64748b" }}>Salas vinculadas a una ubicación. Los horarios operativos se administran en la sección dedicada.</p>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      <form onSubmit={submitRoom} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <select value={roomLocationId} onChange={(event) => setRoomLocationId(event.target.value)} required>
          <option value="">Ubicación</option>
          {locations.map((location) => (
            <option key={location.id} value={location.id}>
              #{location.id} - {location.name}
            </option>
          ))}
        </select>
        <input value={roomCode} onChange={(event) => setRoomCode(event.target.value)} placeholder="Código" required />
        <button type="submit">Agregar</button>
      </form>
      <ul style={{ paddingLeft: 20 }}>
        {rooms.map((item) => (
          <li key={item.id} style={{ marginBottom: 8 }}>
            #{item.id} - Ubic. {item.location_id} - {item.code}{" "}
            <button type="button" onClick={() => removeItem(item.id)}>
              eliminar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
