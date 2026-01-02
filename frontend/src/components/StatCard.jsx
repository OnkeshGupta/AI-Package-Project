export default function StatCard({ title, value }) {
  return (
    <div
      className="
  bg-zinc-900 border border-zinc-800 rounded-xl p-6
  transition-all duration-300
  hover:-translate-y-1 hover:border-indigo-500/40
  hover:shadow-[0_0_30px_-10px_rgba(99,102,241,0.4)]
"
    >
      <p className="text-gray-400 text-sm">{title}</p>
      <h3 className="text-3xl font-bold mt-2">{value}</h3>
    </div>
  );
}