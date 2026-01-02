const API_BASE = "http://localhost:8000";

export async function fetchHistory(token) {
  const res = await fetch(`${API_BASE}/api/history`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to load history");
  }

  return res.json();
}

export async function fetchHistoryDetail(sessionId, token) {
  const res = await fetch(`${API_BASE}/api/history/${sessionId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) throw new Error("Failed to load session details");
  return res.json();
}

export async function deleteHistorySession(sessionId, token) {
  const res = await fetch(`http://127.0.0.1:8000/api/history/${sessionId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to delete history");
  }

  return res.json();
}