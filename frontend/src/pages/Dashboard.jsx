import React, { useEffect, useState, useCallback } from 'react';
import { fetchFridgeStatus } from '../utils/api';
import SensorCard from '../components/SensorCard';
import FoodItem from '../components/FoodItem';
import AiAnalysisTabs from '../components/AiAnalysisTabs';
import ChatInterface from '../components/ChatInterface';
import UserItemsManager from '../components/UserItemsManager';

/**
 * Helper function to determine sensor status based on values
 */
const getSensorStatus = (type, value) => {
  switch (type) {
    case 'temp':
      if (value < 2 || value > 7) return 'danger';
      if (value < 3 || value > 6) return 'warning';
      return 'normal';
    case 'humidity':
      if (value < 40 || value > 75) return 'danger';
      if (value < 45 || value > 70) return 'warning';
      return 'normal';
    case 'gas':
      if (value > 300) return 'danger';
      if (value > 200) return 'warning';
      return 'normal';
    default:
      return 'normal';
  }
};

/**
 * Smart Fridge Dashboard page component
 */
const Dashboard = () => {
  // State for fridge data, loading status and errors
  const [fridgeData, setFridgeData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showChat, setShowChat] = useState(false);
  
  // User management state
  const [currentUser, setCurrentUser] = useState('');
  const [userItems, setUserItems] = useState([]);
  const [loadingUserItems, setLoadingUserItems] = useState(false);
  const [userError, setUserError] = useState(null);

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('fridgeUsername');
    if (savedUser) {
      setCurrentUser(savedUser);
    }
  }, []);

  // Fetch user items when current user changes
  useEffect(() => {
    if (currentUser) {
      fetchUserItems();
    } else {
      setUserItems([]);
    }
  }, [currentUser]);

  // Fetch user items from API
  const fetchUserItems = useCallback(async () => {
    if (!currentUser) return;
    
    try {
      setLoadingUserItems(true);
      setUserError(null);
      
      const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/user/${currentUser}/items`);
      
      if (response.ok) {
        const items = await response.json();
        setUserItems(items);
      } else if (response.status === 404) {
        // User not found, but that's okay - they just don't have items yet
        setUserItems([]);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (err) {
      setUserError('Failed to load user items');
      console.error('Error fetching user items:', err);
    } finally {
      setLoadingUserItems(false);
    }
  }, [currentUser]);

  // Add item to user's fridge
  const addUserItem = async (itemData) => {
    if (!currentUser) return false;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/user/${currentUser}/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(itemData)
      });
      
      if (response.ok) {
        await fetchUserItems(); // Refresh items
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error adding item:', err);
      return false;
    }
  };

  // Delete item from user's fridge
  const deleteUserItem = async (itemId) => {
    if (!currentUser) return false;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/user/${currentUser}/items/${itemId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        await fetchUserItems(); // Refresh items
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error deleting item:', err);
      return false;
    }
  };

  // Handle user selection
  const handleUserChange = (username) => {
    setCurrentUser(username);
    if (username) {
      localStorage.setItem('fridgeUsername', username);
    } else {
      localStorage.removeItem('fridgeUsername');
    }
  };

  // Fetch data on component mount
  useEffect(() => {
    const loadFridgeData = async () => {
      try {
        setIsLoading(true);
        const data = await fetchFridgeStatus();
        setFridgeData(data);
        setError(null);
      } catch (err) {
        setError('Failed to load fridge data. Please try again later.');
        console.error('Error loading fridge data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadFridgeData();

    // Refresh data every 5 minutes
    const intervalId = setInterval(loadFridgeData, 5 * 60 * 1000);
    return () => clearInterval(intervalId);
  }, []);

  // Display loading state
  if (isLoading && !fridgeData) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-3 text-gray-600">Loading Smart Fridge data...</p>
        </div>
      </div>
    );
  }

  // Display error state
  if (error && !fridgeData) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center text-red-600 p-4 bg-red-50 rounded-lg shadow-sm">
          <p className="text-xl">❌ {error}</p>
          <button 
            className="mt-3 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // If we have data, display the dashboard
  return (
    <div className="min-h-screen bg-gray-50 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Smart Fridge Dashboard</h1>
            {fridgeData?.timestamp && (
              <p className="text-sm text-gray-500">
                Last updated: {new Date(fridgeData.timestamp).toLocaleString()}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onClick={() => setShowChat(!showChat)}
            >
              {showChat ? 'Hide Chat' : 'Chat with Fridge'}
            </button>
          </div>
        </header>

        {/* User Selection and Items Management */}
        <section className="mb-8">
          <UserItemsManager
            currentUser={currentUser}
            onUserChange={handleUserChange}
            userItems={userItems}
            onRefreshItems={fetchUserItems}
            onAddItem={addUserItem}
            onDeleteItem={deleteUserItem}
            loading={loadingUserItems}
            error={userError}
          />
        </section>

        {/* Chat Interface - conditionally rendered */}
        {showChat && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-gray-700 mb-3">Chat with Your Fridge</h2>
            <ChatInterface fridgeData={fridgeData} currentUser={currentUser} />
          </section>
        )}

        {/* Sensor Cards */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">Sensor Readings</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <SensorCard 
              title="Temperature" 
              value={fridgeData?.temp} 
              unit="°C" 
              icon="🌡️"
              status={getSensorStatus('temp', fridgeData?.temp)}
            />
            <SensorCard 
              title="Humidity" 
              value={fridgeData?.humidity} 
              unit="%" 
              icon="💧"
              status={getSensorStatus('humidity', fridgeData?.humidity)}
            />
            <SensorCard 
              title="Gas Level" 
              value={fridgeData?.gas} 
              unit="ppm" 
              icon="☁️"
              status={getSensorStatus('gas', fridgeData?.gas)}
            />
          </div>
        </section>

        {/* Food Items */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">Detected Food Items</h2>
          {fridgeData?.items && fridgeData.items.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-3">
              {fridgeData.items.map((item, index) => (
                <FoodItem key={`${item}-${index}`} name={item} />
              ))}
            </div>
          ) : (
            <p className="text-gray-500 bg-white p-4 rounded-lg shadow-sm">
              No food items detected in your fridge.
            </p>
          )}
        </section>

        {/* AI Analysis */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">AI Analysis</h2>
          {fridgeData?.analysis ? (
            <AiAnalysisTabs 
              analysis={fridgeData.analysis}
              priority={fridgeData.priority || ['safety', 'freshness', 'recipes']}
              aiResponse={fridgeData.ai_response}
            />
          ) : (
            <p className="text-gray-500 bg-white p-4 rounded-lg shadow-sm">
              AI analysis not available.
            </p>
          )}
        </section>

        {/* Footer */}
        <footer className="text-center text-gray-500 text-xs mt-12">
          <p>Smart Fridge AI Dashboard &copy; {new Date().getFullYear()}</p>
        </footer>
      </div>
    </div>
  );
};

export default Dashboard; 