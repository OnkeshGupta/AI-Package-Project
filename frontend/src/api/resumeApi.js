const API_BASE = "http://localhost:8000";

export async function rankAndScoreResumes(files, jobDescription, token) {
  const formData = new FormData();

  formData.append("jd_text", jobDescription);

  files.forEach((file) => {
    formData.append("files", file);
  });

  const res = await fetch(`${API_BASE}/api/rank_and_score`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to analyze resumes");
  }

  return res.json();
}