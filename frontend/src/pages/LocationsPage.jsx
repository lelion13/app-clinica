import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";

export function LocationsPage() {
  const [error, setError] = useState("");
  const [locations, setLocations] = useState([]);
  const [locationName, setLocationName] = useState("");

  const load = async () => {
    setError("");
    await safeLoad("/locations", setLocations, setError);
  };

  useEffect(() => {
    load();
  }, []);

  const submitLocation = async (event) => {
    event.preventDefault();
    await apiRequestWithRefresh("/locations", {
      method: "POST",
      body: JSON.stringify({ name: locationName }),
    });
    setLocationName("");
    await load();
  };

  const removeItem = async (id) => {
    await apiRequestWithRefresh(`/locations/${id}`, { method: "DELETE" });
    await load();
  };

  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#fff" }}>
      <h1 style={{ marginTop: 0, fontSize: "1.35rem" }}>Ubicaciones</h1>
      <p style={{ color: "#64748b" }}>Sedes o puntos físicos donde hay consultorios.</p>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      <form onSubmit={submitLocation} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <input
          value={locationName}
          onChange={(event) => setLocationName(event.target.value)}
          placeholder="Nombre"
          required
          style={{ minWidth: 220 }}
        />
        <button type="submit">Agregar</button>
      </form>
      <ul style={{ paddingLeft: 20 }}>
        {locations.map((item) => (
          <li key={item.id} style={{ marginBottom: 8 }}>
            #{item.id} - {item.name}{" "}
            <button type="button" onClick={() => removeItem(item.id)}>
              eliminar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
