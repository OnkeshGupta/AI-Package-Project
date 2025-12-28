import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { fetchHistoryDetail } from "../api/historyApi";
import { useAuth } from "../auth/AuthContext";

export default function HistoryDetail() {
  const { sessionId } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchHistoryDetail(sessionId, token);
        setData(res);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    if (token) load();
  }, [sessionId, token]);

  if (loading) return <p className="text-gray-400 ml-64 p-10">Loading...</p>;
  if (error) return <p className="text-red-400 ml-64 p-10">{error}</p>;

  return (
    <div className="min-h-screen bg-black text-white ml-64 px-12 py-10">
      <Sidebar />

      <button
        onClick={() => navigate("/history")}
        className="mb-6 text-indigo-400 hover:underline"
      >
        ← Back to History
      </button>

      <h1 className="text-3xl font-bold mb-4">Analysis Details</h1>

      <p className="text-gray-400 mb-6">
        {new Date(data.created_at).toLocaleString()}
      </p>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-10">
        <h3 className="font-semibold mb-2">Job Description</h3>
        <p className="text-gray-300 whitespace-pre-wrap">
          {data.job_description}
        </p>
      </div>

      <div className="space-y-6">
        {data.ranked_candidates
          .sort((a, b) => b.final_score - a.final_score)
          .map((candidate, index) => (
            <div
              key={index}
              className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:shadow-lg transition"
            >
              <h3 className="text-lg font-semibold">
                #{index + 1} — {candidate.filename}
                {index === 0 && (
                  <span className="ml-3 px-3 py-1 text-xs rounded-full bg-indigo-500/20 text-indigo-400">
                    Top Match
                  </span>
                )}
              </h3>

              <p className="text-sm text-gray-400 mt-1">
                Verdict: {candidate.feedback.verdict}
              </p>

              {/* SCORE BAR */}
              <div className="mt-4">
                <div className="w-full h-2 bg-zinc-800 rounded-full">
                  <div
                    className="h-full bg-indigo-500 rounded-full"
                    style={{ width: `${candidate.final_score}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  Score: {candidate.final_score.toFixed(1)}%
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <p className="text-sm text-gray-400">Matched Skills</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {candidate.matched_skills.map((s, i) => (
                      <span
                        key={i}
                        className="px-3 py-1 text-xs rounded-full bg-green-500/10 text-green-400"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-sm text-gray-400">Missing Skills</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {candidate.missing_skills.map((s, i) => (
                      <span
                        key={i}
                        className="px-3 py-1 text-xs rounded-full bg-red-500/10 text-red-400"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}