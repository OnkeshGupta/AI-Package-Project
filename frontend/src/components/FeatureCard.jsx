export default function FeatureCard({ title, description }) {
  return (
    <div
      className="
    bg-zinc-900 border border-zinc-800 rounded-2xl p-6
    transition-all duration-300 ease-out
    hover:-translate-y-3 hover:scale-[1.02]
    hover:border-indigo-500/40
    hover:shadow-[0_20px_40px_-15px_rgba(99,102,241,0.4)]
  "
    >
      {/* Glow layer */}
      <div
        className="
          absolute inset-0 rounded-2xl
          opacity-0 group-hover:opacity-100
          transition duration-300
          bg-gradient-to-br from-indigo-500/10 to-purple-500/10
          pointer-events-none
        "
      />

      <h3 className="relative text-xl font-semibold text-white">{title}</h3>

      <p className="relative mt-4 text-gray-300">{description}</p>
    </div>
  );
}
