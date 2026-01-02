export default function DashboardHeader() {
  return (
    <div className="flex justify-between items-center mb-10">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-400 mt-1">
          Upload resumes and get AI-powered rankings instantly.
        </p>
      </div>

      <button
        className="
  mt-6 border border-indigo-500 text-indigo-400
  px-6 py-3 rounded-lg
  hover:bg-indigo-500 hover:text-white
  transition
"
      >
        Upload Resumes
      </button>
    </div>
  );
}