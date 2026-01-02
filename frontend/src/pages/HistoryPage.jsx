import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { fetchHistory, deleteHistorySession } from "../api/historyApi";
import { useAuth } from "../auth/AuthContext";
import { useNavigate } from "react-router-dom";

export default function HistoryPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchHistory(token);
        setHistory(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    if (token) load();
  }, [token]);

  const handleDelete = async (e, sessionId) => {
    e.stopPropagation(); 

    if (!window.confirm("Delete this analysis permanently?")) return;

    try {
      await deleteHistorySession(sessionId, token);
      setHistory((prev) =>
        prev.filter((item) => item.session_id !== sessionId)
      );
    } catch (err) {
      alert("Failed to delete history");
    }
  };

  return (
    <div className="min-h-screen bg-black text-white ml-64 px-12 py-10">
      <Sidebar />

      <h1 className="text-3xl font-bold mb-8">Analysis History</h1>

      {loading && <p className="text-gray-400">Loading history...</p>}
      {error && <p className="text-red-400">{error}</p>}
      {!loading && history.length === 0 && (
        <p className="text-gray-500">No history found.</p>
      )}

      <div className="space-y-6 max-w-4xl">
        {history.map((item) => (
          <div
            key={item.session_id}
            onClick={() => navigate(`/history/${item.session_id}`)}
            className="
              cursor-pointer
              bg-zinc-900 border border-zinc-800 rounded-xl p-6
              transition-all duration-300
              hover:-translate-y-1
              hover:border-indigo-500/50
              hover:shadow-[0_0_40px_rgba(99,102,241,0.25)]
            "
          >
            {/* TOP ROW */}
            <div className="flex justify-between items-start">
              <p className="text-gray-300 max-w-xl">
                {item.job_description.slice(0, 120)}...
              </p>

              {/* DELETE BUTTON */}
              <button
                onClick={(e) => handleDelete(e, item.session_id)}
                className="text-sm text-red-400 hover:text-red-500 transition"
              >
                Delete
              </button>
            </div>

            {/* SCORE */}
            <p className="text-indigo-400 font-semibold mt-2">
              Top Score: {item.top_score.toFixed(1)}%
            </p>

            {/* META */}
            <div className="flex justify-between text-sm text-gray-500 mt-3">
              <span>{item.total_candidates} candidates</span>
              <span>
                {new Intl.DateTimeFormat("en-IN", {
                  dateStyle: "medium",
                  timeZone: "Asia/Kolkata",
                }).format(new Date(item.created_at))}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}