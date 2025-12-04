export default function About() {
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-blue-400 mb-6">About</h1>

      <div className="bg-gray-800 rounded-xl p-6 space-y-4">
        <div className="flex justify-between items-center py-2 border-b border-gray-700">
          <span className="text-gray-400">Framework</span>
          <span className="text-white font-medium">Electron</span>
        </div>
        <div className="flex justify-between items-center py-2 border-b border-gray-700">
          <span className="text-gray-400">Build Tool</span>
          <span className="text-white font-medium">Electron Forge + Vite</span>
        </div>
        <div className="flex justify-between items-center py-2 border-b border-gray-700">
          <span className="text-gray-400">UI Framework</span>
          <span className="text-white font-medium">React 19</span>
        </div>
        <div className="flex justify-between items-center py-2 border-b border-gray-700">
          <span className="text-gray-400">Styling</span>
          <span className="text-white font-medium">Tailwind CSS v4</span>
        </div>
        <div className="flex justify-between items-center py-2">
          <span className="text-gray-400">Language</span>
          <span className="text-white font-medium">TypeScript</span>
        </div>
      </div>
    </div>
  );
}
