import { Link, useLocation } from "react-router-dom";

export default function Sidebar() {
  const location = useLocation();

  const isActive = (path) => location.pathname.startsWith(path);

  const navItem = (label, path) => (
    <Link
      to={path}
      className={`relative flex items-center px-3 py-2 rounded-lg transition
        ${
          isActive(path)
            ? "text-white font-medium bg-indigo-500/10"
            : "text-gray-400 hover:text-white hover:bg-zinc-800"
        }
      `}
    >
      {isActive(path) && (
        <span className="absolute -left-3 h-6 w-1 bg-indigo-500 rounded-full" />
      )}
      {label}
    </Link>
  );

  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 h-screen fixed left-0 top-0 px-6 py-8">
      {/* LOGO */}
      <h2 className="text-xl font-bold mb-10">
        TalentLens<span className="text-indigo-500">.AI</span>
      </h2>

      {/* NAV */}
      <nav className="space-y-2">
        {navItem("Dashboard", "/upload")}
        {navItem("History", "/history")}
      </nav>
    </aside>
  );
}