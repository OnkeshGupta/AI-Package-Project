import { useState } from "react";
import Sidebar from "../components/Sidebar";
import { rankAndScoreResumes } from "../api/resumeApi";
import { useAuth } from "../auth/AuthContext";
import { useNavigate } from "react-router-dom";

export default function UploadResumes() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [jobDescription, setJobDescription] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // ---------- FILE HANDLERS ----------
  const addFiles = (newFiles) => {
    setFiles((prev) => {
      const existingNames = new Set(prev.map((f) => f.name));
      const unique = newFiles.filter((f) => !existingNames.has(f.name));
      return [...prev, ...unique];
    });
  };

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files).filter(
      (file) => file.type === "application/pdf"
    );
    addFiles(selected);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const dropped = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === "application/pdf"
    );
    addFiles(dropped);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // ---------- ANALYZE ----------
  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    try {
      if (!token) {
        throw new Error("Not authenticated");
      }

      const data = await rankAndScoreResumes(files, jobDescription, token);
      if (!data.session_id) {
        throw new Error("Session ID not returned from server");
      }
      navigate(`/history/${data.session_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white ml-64">
      <Sidebar />

      <main className="px-12 py-10 max-w-5xl">
        {/* HEADER */}
        <div className="mb-12">
          <h1 className="text-3xl font-bold">Upload & Match Resumes</h1>
          <p className="text-gray-400 mt-2">
            Upload resumes and match them against a job description using AI.
          </p>
        </div>

        <div className="space-y-14">
          {/* STEP 1 */}
          <section>
            <h2 className="text-lg font-semibold mb-4">
              1. Upload Resumes (PDF)
            </h2>

            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onDragEnter={() => setDragActive(true)}
              onDragLeave={() => setDragActive(false)}
              className={`border-2 border-dashed rounded-xl p-12 text-center bg-zinc-900 transition-all duration-300 ${
                dragActive
                  ? "border-indigo-500 bg-indigo-500/10 shadow-[0_0_40px_rgba(99,102,241,0.35)]"
                  : "border-indigo-500/40 hover:border-indigo-500 hover:shadow-[0_0_30px_rgba(99,102,241,0.15)]"
              }`}
            >
              <p className="text-gray-300 mb-2">Drag & drop PDF resumes here</p>
              <p className="text-sm text-gray-500 mb-6">
                or click to browse files
              </p>

              <label>
                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  className="hidden"
                  onChange={handleFileSelect}
                />
                <span className="px-6 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 cursor-pointer font-medium transition">
                  Select Files
                </span>
              </label>

              {files.length > 0 && (
                <div className="mt-6 space-y-3 text-left">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3"
                    >
                      <div>
                        <p className="text-sm font-medium text-gray-200">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>

                      <button
                        onClick={() => removeFile(index)}
                        className="text-red-400 hover:text-red-500 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* STEP 2 */}
          <section>
            <h2 className="text-lg font-semibold mb-4">2. Job Description</h2>

            <textarea
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className="w-full h-48 bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
            />
          </section>

          {/* STEP 3 */}
          <section>
            <button
              onClick={handleAnalyze}
              disabled={loading || files.length === 0 || !jobDescription}
              className={`w-full py-4 rounded-xl text-lg font-semibold transition-all duration-300 ${
                loading || files.length === 0 || !jobDescription
                  ? "bg-zinc-800 text-gray-500 cursor-not-allowed"
                  : "bg-indigo-600 hover:bg-indigo-500 hover:shadow-[0_0_30px_rgba(99,102,241,0.35)]"
              }`}
            >
              {loading ? "Analyzing..." : "Analyze & Rank Candidates"}
            </button>
          </section>

          {/* ERROR */}
          {error && (
            <div className="mt-4 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              {error.includes("401")
                ? "Session expired. Please log in again."
                : error}
            </div>
          )}

          {/* RESULTS */}
          {result && (
            <section className="mt-16">
              <h2 className="text-2xl font-bold mb-6">
                Ranked Candidates ({result.total_resumes})
              </h2>

              <div className="space-y-6">
                {result.ranked_candidates
                  .sort((a, b) => b.final_score - a.final_score)
                  .map((candidate, index) => (
                    <div
                      key={index}
                      className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 transition-all duration-300 hover:-translate-y-1 hover:border-indigo-500/50 hover:shadow-[0_0_40px_rgba(99,102,241,0.25)]"
                    >
                      {/* HEADER */}
                      <div className="flex justify-between items-center mb-4">
                        <div>
                          <h3 className="text-lg font-semibold">
                            #{index + 1} — {candidate.filename}
                            {index === 0 && (
                              <span className="ml-3 px-3 py-1 text-xs rounded-full bg-indigo-500/20 text-indigo-400">
                                Top Match
                              </span>
                            )}
                          </h3>
                          <p className="text-sm text-gray-400">
                            Verdict:{" "}
                            <span className="text-indigo-400 font-medium">
                              {candidate.feedback.verdict}
                            </span>
                          </p>
                        </div>

                        <div className="text-right">
                          <p className="text-sm text-gray-400">Final Score</p>
                          <p className="text-2xl font-bold text-indigo-400">
                            {candidate.final_score}
                          </p>

                          {/* SCORE BAR */}
                          <div className="mt-4">
                            <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-700 ${
                                  candidate.final_score >= 75
                                    ? "bg-green-500"
                                    : candidate.final_score >= 50
                                    ? "bg-yellow-400"
                                    : "bg-red-500"
                                }`}
                                style={{ width: `${candidate.final_score}%` }}
                              />
                            </div>

                            <p className="text-xs text-gray-400 mt-1">
                              Match Strength: {candidate.final_score.toFixed(1)}
                              %
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* SKILLS */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <p className="text-sm text-gray-400 mb-2">
                            Matched Skills
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {candidate.matched_skills.map((skill, i) => (
                              <span
                                key={i}
                                className="px-3 py-1 text-xs rounded-full bg-green-500/10 text-green-400"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div>
                          <p className="text-sm text-gray-400 mb-2">
                            Missing Skills
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {candidate.missing_skills.map((skill, i) => (
                              <span
                                key={i}
                                className="px-3 py-1 text-xs rounded-full bg-red-500/10 text-red-400"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* SUMMARY */}
                      <p className="mt-4 text-sm text-gray-400">
                        {candidate.feedback.summary}
                      </p>
                    </div>
                  ))}
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
