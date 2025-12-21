export default function Sidebar() {
  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 h-screen fixed left-0 top-0 px-6 py-8">
      <h2 className="text-xl font-bold mb-10">
        TalentLens<span className="text-indigo-500">.AI</span>
      </h2>

      <nav className="space-y-4 text-gray-400">
        <div className="relative text-white font-medium">
          <span className="absolute -left-3 top-1/2 -translate-y-1/2 h-6 w-1 bg-indigo-500 rounded-full" />
          Dashboard
        </div>
        <div className="hover:text-white cursor-pointer">Upload Resumes</div>
        <div className="hover:text-white cursor-pointer">Rankings</div>
        <div className="hover:text-white cursor-pointer">History</div>
      </nav>
    </aside>
  );
}
