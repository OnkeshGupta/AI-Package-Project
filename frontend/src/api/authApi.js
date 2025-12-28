const API_BASE = "http://localhost:8000";

/**
 * REGISTER
 * Backend expects JSON body
 */
export async function registerUser(email, password) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || "Registration failed");
  }

  return res.json();
}

/**
 * LOGIN
 * Backend expects FORM DATA (OAuth2PasswordRequestForm)
 */
export async function loginUser(email, password) {
  const form = new FormData();
  form.append("username", email); // MUST be username
  form.append("password", password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || "Login failed");
  }

  return res.json(); // { access_token, token_type }
}