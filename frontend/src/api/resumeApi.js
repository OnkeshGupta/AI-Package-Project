export async function rankAndScoreResumes(files, jobDescription) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  formData.append("jd_text", jobDescription);

  const response = await fetch("http://localhost:8000/api/rank_and_score", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Failed to analyze resumes");
  }

  return response.json();
}