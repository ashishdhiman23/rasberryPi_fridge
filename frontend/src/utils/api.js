/**
 * API utilities for Smart Fridge Dashboard
 */

// API base URL - change to actual backend URL in production
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : '/mock.json';

/**
 * Fetches the current fridge status from the API
 * @returns {Promise<Object>} The fridge status data
 */
export const fetchFridgeStatus = async () => {
  try {
    // In development, we'll use the mock data
    if (process.env.NODE_ENV !== 'production') {
      const response = await fetch(API_BASE_URL);
      return await response.json();
    }

    // In production, use the actual API endpoint
    const response = await fetch(`${API_BASE_URL}/fridge-status`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching fridge status:', error);
    throw error;
  }
}; 