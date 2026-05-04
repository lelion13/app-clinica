function normalizeApiBaseUrl(raw) {
  if (!raw) return "";
  return String(raw).replace(/\/+$/, "");
}

// Produccion (mismo dominio): dejar VITE_API_BASE_URL vacio => usa `/api/v1` (same-origin).
// Desarrollo: `VITE_API_BASE_URL=http://localhost:8000/api/v1`
const API_BASE_URL =
  normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL) || "/api/v1";

async function parseError(response) {
  let message = "Error inesperado";
  let detail = null;
  const raw = await response.text();
  if (raw) {
    try {
      const data = JSON.parse(raw);
      if (typeof data.detail === "string") message = data.detail;
      else if (typeof data.message === "string") message = data.message;
      detail = data.detail ?? null;
    } catch {
      message = raw;
    }
  }
  const error = new Error(message);
  error.status = response.status;
  error.detail = detail;
  return error;
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  if (response.status === 204) return null;
  return response.json();
}

export async function apiRequestWithRefresh(path, options = {}) {
  try {
    return await apiRequest(path, options);
  } catch (error) {
    if (error.status !== 401) {
      throw error;
    }
    try {
      await apiRequest("/auth/refresh", { method: "POST" });
      return apiRequest(path, options);
    } catch {
      throw error;
    }
  }
}
