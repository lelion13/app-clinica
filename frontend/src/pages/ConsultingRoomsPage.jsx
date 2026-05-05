import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

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
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Consultorios</h1>
      <p style={uiStyles.helpText}>Salas vinculadas a una ubicación. Los horarios operativos se administran en la sección dedicada.</p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      <form onSubmit={submitRoom} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <select value={roomLocationId} onChange={(event) => setRoomLocationId(event.target.value)} required style={uiStyles.formControl}>
          <option value="">Ubicación</option>
          {locations.map((location) => (
            <option key={location.id} value={location.id}>
              #{location.id} - {location.name}
            </option>
          ))}
        </select>
        <input value={roomCode} onChange={(event) => setRoomCode(event.target.value)} placeholder="Código" required style={uiStyles.formControl} />
        <button type="submit" style={uiStyles.buttonPrimary}>Agregar</button>
      </form>
      <ul style={uiStyles.listCard}>
        {rooms.map((item) => (
          <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
            #{item.id} - Ubic. {item.location_id} - {item.code}{" "}
            <button type="button" onClick={() => removeItem(item.id)} style={{ ...uiStyles.buttonDanger, marginLeft: 8 }}>
              eliminar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
