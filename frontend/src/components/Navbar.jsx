export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 w-full z-50 bg-black border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">
          TalentLens<span className="text-indigo-500">.AI</span>
        </h1>

        <div className="space-x-6 text-sm text-gray-300">
          <a href="#" className="hover:text-white transition">Features</a>
          <a href="#" className="hover:text-white transition">Pricing</a>
          <a href="#" className="hover:text-white transition">Login</a>
        </div>
      </div>
    </nav>
  );
}