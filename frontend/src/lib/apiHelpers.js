import { apiRequestWithRefresh } from "../services/api";

/** Loads JSON from API and stores in setter; captures message on failure. */
export async function safeLoad(path, setData, setError) {
  try {
    const data = await apiRequestWithRefresh(path);
    setData(data);
  } catch (err) {
    setError(err.message);
  }
}
