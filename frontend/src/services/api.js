const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

async function parseError(response) {
  let message = "Error inesperado";
  try {
    const data = await response.json();
    message = data.detail || data.message || message;
  } catch {
    const text = await response.text();
    if (text) message = text;
  }
  const error = new Error(message);
  error.status = response.status;
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
