import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 w-full z-[100] bg-black border-b border-white/10 pointer-events-auto">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">
          TalentLens<span className="text-indigo-500">.AI</span>
        </Link>

        <div className="space-x-6 text-sm text-gray-300">
          <a href="#" className="hover:text-white transition">
            Features
          </a>
          <a href="#" className="hover:text-white transition">
            Pricing
          </a>
          <Link to="/login" className="hover:text-white transition">
            Login
          </Link>
          <Link to="/register" className="hover:text-white transition">
            Register
          </Link>
        </div>
      </div>
    </nav>
  );
}
