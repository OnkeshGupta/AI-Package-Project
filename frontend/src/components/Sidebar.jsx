import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Sidebar() {
  const location = useLocation();
  const { logout } = useAuth();

  const navItem = (path) =>
    `relative flex items-center px-3 py-2 rounded-lg transition
     ${
       location.pathname === path
         ? "text-white bg-zinc-900 font-medium"
         : "text-gray-400 hover:text-white hover:bg-zinc-900"
     }`;

  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 h-screen fixed left-0 top-0 px-6 py-8">
      {/* LOGO */}
      <h2 className="text-xl font-bold mb-10">
        TalentLens<span className="text-indigo-500">.AI</span>
      </h2>

      {/* NAV */}
      <nav className="space-y-2">
        <Link to="/upload" className={navItem("/upload")}>
          {location.pathname === "/upload" && (
            <span className="absolute -left-3 h-6 w-1 bg-indigo-500 rounded-full" />
          )}
          Upload Resumes
        </Link>

        <Link to="/history" className={navItem("/history")}>
          {location.pathname === "/history" && (
            <span className="absolute -left-3 h-6 w-1 bg-indigo-500 rounded-full" />
          )}
          History
        </Link>

        {/* DIVIDER */}
        <div className="border-t border-zinc-800 my-6" />

        {/* LOGOUT */}
        <button
          onClick={logout}
          className="flex items-center px-3 py-2 text-red-400 hover:text-red-500 hover:bg-zinc-900 rounded-lg transition w-full"
        >
          Logout
        </button>
      </nav>
    </aside>
  );
}