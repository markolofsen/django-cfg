import { useState } from 'react';

export default function Settings() {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [autoUpdate, setAutoUpdate] = useState(false);

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-blue-400 mb-6">Settings</h1>

      <div className="bg-gray-800 rounded-xl p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-white font-medium">Dark Mode</h3>
            <p className="text-gray-400 text-sm">Enable dark theme</p>
          </div>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`w-12 h-6 rounded-full transition-colors ${
              darkMode ? 'bg-blue-500' : 'bg-gray-600'
            }`}
          >
            <div
              className={`w-5 h-5 bg-white rounded-full transition-transform ${
                darkMode ? 'translate-x-6' : 'translate-x-0.5'
              }`}
            />
          </button>
        </div>

        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-white font-medium">Notifications</h3>
            <p className="text-gray-400 text-sm">Receive desktop notifications</p>
          </div>
          <button
            onClick={() => setNotifications(!notifications)}
            className={`w-12 h-6 rounded-full transition-colors ${
              notifications ? 'bg-blue-500' : 'bg-gray-600'
            }`}
          >
            <div
              className={`w-5 h-5 bg-white rounded-full transition-transform ${
                notifications ? 'translate-x-6' : 'translate-x-0.5'
              }`}
            />
          </button>
        </div>

        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-white font-medium">Auto Update</h3>
            <p className="text-gray-400 text-sm">Automatically check for updates</p>
          </div>
          <button
            onClick={() => setAutoUpdate(!autoUpdate)}
            className={`w-12 h-6 rounded-full transition-colors ${
              autoUpdate ? 'bg-blue-500' : 'bg-gray-600'
            }`}
          >
            <div
              className={`w-5 h-5 bg-white rounded-full transition-transform ${
                autoUpdate ? 'translate-x-6' : 'translate-x-0.5'
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  );
}
