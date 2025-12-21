import Sidebar from "../components/Sidebar";
import DashboardHeader from "../components/DashboardHeader";
import StatCard from "../components/StatCard";
import EmptyState from "../components/EmptyState";

export default function Dashboard() {
  return (
    <div className="bg-black text-white min-h-screen">
      <Sidebar />

      <main className="ml-64 px-10 py-10 animate-fadeIn">
        <DashboardHeader />

        {/* STATS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <StatCard title="Resumes Uploaded" value="0" />
          <StatCard title="Jobs Created" value="0" />
          <StatCard title="Candidates Ranked" value="0" />
        </div>

        {/* MAIN CONTENT */}
        <EmptyState />
      </main>
    </div>
  );
}