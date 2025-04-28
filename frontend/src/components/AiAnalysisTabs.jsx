import React, { useState } from 'react';

/**
 * AI Analysis Tabs component for showing different types of AI analysis
 * 
 * @param {Object} props - Component props
 * @param {Object} props.analysis - Analysis object with different categories
 * @param {Array} props.priority - Order of priority for the tabs
 * @param {string} props.aiResponse - Overall AI response message
 */
const AiAnalysisTabs = ({ analysis, priority = ['safety', 'freshness', 'recipes'], aiResponse }) => {
  // Set the first tab as active by default (based on priority)
  const [activeTab, setActiveTab] = useState(priority[0] || 'safety');

  // Emoji mapping for tab icons
  const tabIcons = {
    safety: '🛡️',
    freshness: '🥬',
    recipes: '🍳',
  };

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      {/* AI Response Header */}
      {aiResponse && (
        <div className="px-4 py-3 bg-blue-50 text-blue-700 border-b border-blue-100">
          <p>{aiResponse}</p>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex border-b">
        {priority.map((tab) => (
          <button
            key={tab}
            className={`flex-1 py-2 px-4 text-sm font-medium focus:outline-none ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab(tab)}
          >
            <span className="mr-1">{tabIcons[tab] || ''}</span>
            <span className="capitalize">{tab}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4">
        {priority.map((tab) => (
          <div key={tab} className={activeTab === tab ? 'block' : 'hidden'}>
            <p>{analysis[tab] || `No ${tab} analysis available.`}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AiAnalysisTabs; 