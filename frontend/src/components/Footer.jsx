import { Link } from "react-router-dom";

export default function CTA() {
  return (
    <section className="py-32 text-center bg-gradient-to-b from-black to-indigo-950">
      <h2 className="text-3xl md:text-4xl font-bold">
        Start Hiring Smarter with AI
      </h2>

      <p className="mt-4 text-gray-400 max-w-xl mx-auto">
        Upload resumes, match candidates, and rank them instantly — powered by
        TalentLens.AI.
      </p>

      <Link
        to="/register"
        className="inline-block mt-8 px-8 py-4 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold transition"
      >
        Get Started Free
      </Link>
    </section>
  );
}