const API_BASE = "http://127.0.0.1:8000";

function extractErrorMessage(data) {
  if (!data) return "Something went wrong";

  // FastAPI validation errors
  if (Array.isArray(data.detail)) {
    return data.detail.map((e) => e.msg).join(", ");
  }

  // Normal string error
  if (typeof data.detail === "string") {
    return data.detail;
  }

  return "Request failed";
}

export async function registerUser(email, password) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const data = await res.json();
    throw new Error(extractErrorMessage(data));
  }

  return res.json();
}

export async function loginUser(email, password) {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const data = await res.json();
    throw new Error(extractErrorMessage(data));
  }

  return res.json(); // { access_token }
}