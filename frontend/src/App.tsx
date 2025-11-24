import React from 'react';
import './App.css';

/**
 * PLACEHOLDER APP COMPONENT
 * 
 * This is a minimal scaffold. You should replace this with your v0.dev components.
 * 
 * Your v0 components should:
 * 1. Import API functions from './lib/api'
 * 2. Use uploadFile(), getScanStatus(), getResults() to interact with the backend
 * 3. Display SecurityFinding[] results matching the data contract
 */

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          SecureScan.ai
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Frontend Scaffold Ready
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-2xl">
          <h2 className="text-xl font-semibold text-blue-900 mb-3">
            🚧 Replace this component with your v0.dev UI
          </h2>
          <ul className="text-left text-sm text-blue-800 space-y-2">
            <li>• Import API functions from <code className="bg-blue-100 px-1 rounded">./lib/api</code></li>
            <li>• Use <code className="bg-blue-100 px-1 rounded">uploadFile()</code> to upload Python files</li>
            <li>• Poll <code className="bg-blue-100 px-1 rounded">getScanStatus()</code> to check progress</li>
            <li>• Display results from <code className="bg-blue-100 px-1 rounded">getResults()</code></li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
