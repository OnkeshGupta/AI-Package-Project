export default function EmptyState() {
  return (
    <div
      className="
  border border-dashed border-zinc-700 rounded-xl p-16 text-center
  bg-gradient-to-br from-zinc-900/60 to-black
"
    >
      <div className="text-4xl mb-4">📄</div>

      <h3 className="text-xl font-semibold">No resumes uploaded yet</h3>

      <p className="text-gray-400 mt-2">
        Upload resumes to start AI-powered candidate ranking.
      </p>

      <button
        className="
    mt-6 bg-indigo-600 px-6 py-3 rounded-lg
    hover:bg-indigo-500 transition
    hover:shadow-[0_0_20px_rgba(99,102,241,0.5)]
  "
      >
        Upload Resume
      </button>
    </div>
  );
}