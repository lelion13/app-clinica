import { useEffect, useState } from "react";

import { apiRequestWithRefresh } from "../services/api";
import { safeLoad } from "../lib/apiHelpers";
import { uiStyles, uiTheme } from "../ui/theme";

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
    <section style={uiStyles.pageSection}>
      <h1 style={uiStyles.sectionTitle}>Ubicaciones</h1>
      <p style={uiStyles.helpText}>Sedes o puntos físicos donde hay consultorios.</p>
      {error ? <p style={{ color: uiTheme.colors.danger }}>{error}</p> : null}
      <form onSubmit={submitLocation} style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <input
          value={locationName}
          onChange={(event) => setLocationName(event.target.value)}
          placeholder="Nombre"
          required
          style={{ ...uiStyles.formControl, minWidth: 220 }}
        />
        <button type="submit" style={uiStyles.buttonPrimary}>Agregar</button>
      </form>
      <ul style={uiStyles.listCard}>
        {locations.map((item) => (
          <li key={item.id} style={{ padding: "8px 10px", borderBottom: `1px solid ${uiTheme.colors.border}` }}>
            #{item.id} - {item.name}{" "}
            <button type="button" onClick={() => removeItem(item.id)} style={{ ...uiStyles.buttonDanger, marginLeft: 8 }}>
              eliminar
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
