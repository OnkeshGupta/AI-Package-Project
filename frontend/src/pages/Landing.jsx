import Navbar from "../components/Navbar";
import FeatureCard from "../components/FeatureCard";
import CTA from "../components/CTA";
import Footer from "../components/Footer";
import AnimatedProcessFlow from "../components/AnimatedProcessFlow";
import Reveal from "../components/Reveal";

export default function Landing() {
  return (
    <div className="bg-black text-white">
      <Navbar />

      {/* HERO */}
      <section className="min-h-[90vh] flex flex-col justify-center items-center px-6 text-center pt-32">
        <Reveal>
          <h1 className="text-4xl md:text-6xl font-bold">
            TalentLens<span className="text-indigo-500">.AI</span>
          </h1>
        </Reveal>

        <Reveal delay={0.1}>
          <p className="mt-6 text-gray-400 max-w-xl">
            AI-powered resume screening, matching, and ranking — built for
            modern hiring.
          </p>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20 max-w-6xl w-full">
          <FeatureCard
            title="Resume Upload"
            description="Upload resumes in seconds with smart parsing."
          />
          <FeatureCard
            title="AI Matching"
            description="Semantic AI matching against job descriptions."
          />
          <FeatureCard
            title="Smart Ranking"
            description="Automatically rank candidates by relevance."
          />
        </div>
      </section>

      <section className="py-32 px-6 max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
          Hiring is broken. TalentLens fixes it.
        </h2>

        <div className="grid md:grid-cols-2 gap-12">
          <div className="border border-red-500/30 rounded-xl p-8">
            <h3 className="text-xl font-semibold text-red-400 mb-4">
              Traditional Hiring
            </h3>
            <ul className="space-y-3 text-gray-400">
              <li>❌ Manually reading hundreds of resumes</li>
              <li>❌ Keyword-based filtering</li>
              <li>❌ Biased shortlisting</li>
              <li>❌ Slow & inconsistent decisions</li>
            </ul>
          </div>

          <div className="border border-indigo-500/40 rounded-xl p-8 bg-indigo-500/5">
            <h3 className="text-xl font-semibold text-indigo-400 mb-4">
              TalentLens.AI
            </h3>
            <ul className="space-y-3 text-gray-300">
              <li>✅ AI-powered semantic understanding</li>
              <li>✅ Skill & experience-aware ranking</li>
              <li>✅ Fair & explainable scoring</li>
              <li>✅ Results in seconds</li>
            </ul>
          </div>
        </div>
      </section>

      <AnimatedProcessFlow />

      <section className="py-32 px-6 max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
          Built for modern hiring teams
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="border border-white/10 rounded-xl p-6">
            <h3 className="font-semibold text-lg mb-2">Recruiters</h3>
            <p className="text-gray-400 text-sm">
              Instantly shortlist the most relevant candidates without manual
              screening.
            </p>
          </div>

          <div className="border border-white/10 rounded-xl p-6">
            <h3 className="font-semibold text-lg mb-2">Startups</h3>
            <p className="text-gray-400 text-sm">
              Hire faster with limited resources and no dedicated HR team.
            </p>
          </div>

          <div className="border border-white/10 rounded-xl p-6">
            <h3 className="font-semibold text-lg mb-2">Hiring Managers</h3>
            <p className="text-gray-400 text-sm">
              Make data-backed hiring decisions with transparent AI insights.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTA />

      {/* FOOTER */}
      <Footer />
    </div>
  );
}
