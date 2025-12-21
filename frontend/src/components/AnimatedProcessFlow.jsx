import { motion, useInView } from "framer-motion";
import { Upload, Brain, BarChart3 } from "lucide-react";
import { useRef } from "react";

export default function AnimatedProcessFlow() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section
      ref={ref}
      className="relative py-32 px-6 bg-black overflow-hidden"
    >
      {/* Animated gradient blob */}
      <motion.div
        className="absolute top-1/2 left-1/2 w-[500px] h-[500px] rounded-full bg-indigo-500/20 blur-3xl"
        initial={{ opacity: 0, scale: 0.6 }}
        animate={isInView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 1.2, ease: "easeOut" }}
        style={{ transform: "translate(-50%, -50%)" }}
      />

      <div className="relative max-w-4xl mx-auto flex flex-col gap-24">
        {/* STEP 1 */}
        <FlowStep
          icon={<Upload size={32} />}
          title="Upload Resumes"
          description="Upload multiple resumes in seconds. TalentLens parses everything automatically."
          isInView={isInView}
          delay={0}
        />

        <FlowLine isInView={isInView} delay={0.3} />

        {/* STEP 2 */}
        <FlowStep
          icon={<Brain size={32} />}
          title="AI Understands the Job"
          description="Our AI semantically understands the job description — not just keywords."
          isInView={isInView}
          delay={0.4}
        />

        <FlowLine isInView={isInView} delay={0.7} />

        {/* STEP 3 */}
        <FlowStep
          icon={<BarChart3 size={32} />}
          title="Smart Ranking"
          description="Candidates are ranked instantly based on relevance and skill match."
          isInView={isInView}
          delay={0.8}
        />
      </div>
    </section>
  );
}

/* ---------------- Subcomponents ---------------- */

function FlowStep({ icon, title, description, isInView, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 60 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, delay }}
      className="flex items-start gap-6"
    >
      <div className="flex items-center justify-center w-14 h-14 rounded-xl border border-white/20 text-indigo-400">
        {icon}
      </div>

      <div>
        <h3 className="text-xl font-semibold">{title}</h3>
        <p className="mt-2 text-gray-400 max-w-md">{description}</p>
      </div>
    </motion.div>
  );
}

function FlowLine({ isInView, delay }) {
  return (
    <motion.div
      initial={{ height: 0, opacity: 0 }}
      animate={isInView ? { height: 80, opacity: 1 } : {}}
      transition={{ duration: 0.6, delay }}
      className="w-px bg-gradient-to-b from-indigo-400/60 to-transparent mx-7"
    />
  );
}