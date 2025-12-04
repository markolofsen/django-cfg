import { useState } from 'react';

export default function Home() {
  const [count, setCount] = useState(0);

  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold text-blue-400 mb-4">
        Electron + React + Tailwind v4
      </h1>
      <p className="text-gray-300 mb-8">
        Built with Electron Forge, Vite, and TypeScript
      </p>

      <div className="bg-gray-800 rounded-xl p-8 max-w-md mx-auto">
        <p className="text-6xl font-bold text-white mb-4">{count}</p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => setCount((c) => c - 1)}
            className="px-6 py-2 bg-red-500 hover:bg-red-600 rounded-lg transition-colors font-medium"
          >
            Decrease
          </button>
          <button
            onClick={() => setCount((c) => c + 1)}
            className="px-6 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors font-medium"
          >
            Increase
          </button>
        </div>
      </div>
    </div>
  );
}
