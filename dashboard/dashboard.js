// Configuration
const API_URL = window.location.origin; // Set API URL to current origin
const REFRESH_INTERVAL = 30000; // 30 seconds
const SESSION_ID = 'dashboard-' + Date.now();
const MAX_RETRY_ATTEMPTS = 3;

// DOM Elements
const apiStatus = document.getElementById('api-status');
const tempValue = document.getElementById('temp-value');
const humidityValue = document.getElementById('humidity-value');
const gasValue = document.getElementById('gas-value');
const lastUpdated = document.getElementById('last-updated');
const fridgeImage = document.getElementById('fridge-image');
const imageTimestamp = document.getElementById('image-timestamp');
const chatMessages = document.getElementById('chat-messages');
const userMessageInput = document.getElementById('user-message');
const sendButton = document.getElementById('send-button');
const includeImageCheckbox = document.getElementById('include-image');
const foodItemsContainer = document.getElementById('food-items-container');

// Global state
let isApiAvailable = false;
let lastUploadData = null;
let isSendingMessage = false;

// Initialize the dashboard
function initDashboard() {
    // Set up event listeners
    sendButton.addEventListener('click', sendMessage);
    userMessageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Check API status immediately
    checkApiStatus();

    // Set up regular data refresh
    setInterval(refreshDashboardData, REFRESH_INTERVAL);
    
    // Initial data load
    refreshDashboardData();
}

// Check if the API is available
async function checkApiStatus() {
    try {
        updateApiStatus('loading', 'Checking API...');
        
        const response = await fetch(`${API_URL}/api/status`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            updateApiStatus('online', 'API: Online');
            isApiAvailable = true;
            return true;
        } else {
            updateApiStatus('offline', 'API: Offline');
            isApiAvailable = false;
            return false;
        }
    } catch (error) {
        console.error('API status check failed:', error);
        updateApiStatus('offline', 'API: Offline');
        isApiAvailable = false;
        return false;
    }
}

// Update the API status indicator
function updateApiStatus(status, message) {
    apiStatus.className = 'status-indicator ' + status;
    apiStatus.textContent = message;
}

// Refresh all dashboard data
async function refreshDashboardData() {
    const isApiUp = await checkApiStatus();
    
    if (isApiUp) {
        // Get sensor data and fridge image
        try {
            const data = await fetchLastUploadData();
            if (data) {
                updateSensorReadings(data);
                updateFridgeImage(data.image);
                updateFoodItems(data);
            }
        } catch (error) {
            console.error('Error refreshing dashboard data:', error);
        }
    }
}

// Fetch the last uploaded data
async function fetchLastUploadData() {
    try {
        const response = await fetch(`${API_URL}/api/last_data`);
        
        if (response.ok) {
            const data = await response.json();
            lastUploadData = data;
            return data;
        }
        
        // Fallback: If we can't get data from API, use mock data
        return getMockData();
    } catch (error) {
        console.error('Error fetching last upload data:', error);
        // Return mock data if API fails
        return getMockData();
    }
}

// Get mock data for testing
function getMockData() {
    // Create mock data with the latest timestamp
    const mockData = {
        temp: (Math.random() * 5 + 2).toFixed(1),
        humidity: (Math.random() * 30 + 40).toFixed(1),
        gas: Math.floor(Math.random() * 200 + 50),
        timestamp: new Date().toISOString(),
        last_seen: {
            "apple": Math.floor(Math.random() * 3),
            "milk": Math.floor(Math.random() * 5),
            "cheese": Math.floor(Math.random() * 7),
            "lettuce": Math.floor(Math.random() * 4)
        }
    };
    
    lastUploadData = mockData;
    return mockData;
}

// Update sensor readings display
function updateSensorReadings(data) {
    tempValue.textContent = data.temp ?? '--';
    humidityValue.textContent = data.humidity ?? '--';
    gasValue.textContent = data.gas ?? '--';
    
    // Format timestamp
    if (data.timestamp) {
        const date = new Date(data.timestamp);
        lastUpdated.textContent = formatDate(date);
    } else {
        lastUpdated.textContent = '--';
    }
    
    // Highlight temperature if outside safe range
    if (data.temp !== null && data.temp !== undefined) {
        if (data.temp > 5 || data.temp < 1) {
            tempValue.className = 'reading-value warning';
        } else {
            tempValue.className = 'reading-value';
        }
    }
}

// Format date as readable string
function formatDate(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + 
           ' ' + date.toLocaleDateString();
}

// Update the fridge image
function updateFridgeImage(imageData) {
    if (imageData && imageData.path) {
        // Use the image path from the API
        const imageUrl = `${API_URL}${imageData.path}`;
        
        // Add timestamp to prevent caching
        fridgeImage.src = `${imageUrl}?t=${Date.now()}`;
        
        // Update timestamp text
        if (imageData.timestamp) {
            const date = new Date(imageData.timestamp);
            imageTimestamp.textContent = 'Last updated: ' + formatDate(date);
        } else {
            imageTimestamp.textContent = 'Last update time unknown';
        }
    } else {
        // No image data available, use placeholder
        fridgeImage.src = 'placeholder-fridge.jpg';
        imageTimestamp.textContent = 'No recent image available';
    }
}

// Update food items display
function updateFoodItems(data) {
    if (!data.last_seen || Object.keys(data.last_seen).length === 0) {
        foodItemsContainer.innerHTML = '<div class="no-items">No food items detected yet</div>';
        return;
    }
    
    let foodItemsHTML = '';
    for (const [item, days] of Object.entries(data.last_seen)) {
        let daysText = '';
        if (days === 0) {
            daysText = 'Today';
        } else if (days === 1) {
            daysText = '1 day ago';
        } else {
            daysText = `${days} days ago`;
        }
        
        foodItemsHTML += `
            <div class="food-item">
                <span class="food-item-name">${item}</span>
                <span class="food-item-days">(${daysText})</span>
            </div>
        `;
    }
    
    foodItemsContainer.innerHTML = foodItemsHTML;
}

// Add a message to the chat
function addMessageToChat(type, content, options = {}) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    
    if (type === 'user') {
        messageElement.classList.add('user-message');
    } else if (type === 'fridge') {
        messageElement.classList.add('fridge-message');
    } else {
        messageElement.classList.add('system-message');
    }
    
    if (options.loading) {
        messageElement.classList.add('loading');
    }
    
    if (options.id) {
        messageElement.id = options.id;
    }
    
    messageElement.textContent = content;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageElement;
}

// Remove a specific message
function removeMessage(id) {
    const message = document.getElementById(id);
    if (message) {
        message.remove();
    }
}

// Send a message to the fridge AI
async function sendMessage() {
    const userMessage = userMessageInput.value.trim();
    
    // Don't send empty messages
    if (!userMessage || isSendingMessage) return;
    
    // Disable input while sending
    isSendingMessage = true;
    sendButton.disabled = true;
    userMessageInput.disabled = true;
    
    // Add user message to chat
    addMessageToChat('user', userMessage);
    
    // Add loading message
    addMessageToChat('system', 'Thinking', { loading: true, id: 'loading-message' });
    
    // Clear input
    userMessageInput.value = '';
    
    // Check if API is available first
    if (!isApiAvailable) {
        const success = await checkApiStatus();
        if (!success) {
            removeMessage('loading-message');
            addMessageToChat('system', 'Sorry, the fridge AI is currently offline. Please try again later.');
            isSendingMessage = false;
            sendButton.disabled = false;
            userMessageInput.disabled = false;
            return;
        }
    }
    
    // Send message to API
    try {
        let attempt = 0;
        let success = false;
        let response;
        
        while (attempt < MAX_RETRY_ATTEMPTS && !success) {
            try {
                response = await fetch(`${API_URL}/api/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_message: userMessage,
                        include_image: includeImageCheckbox.checked,
                        session_id: SESSION_ID
                    })
                });
                
                if (response.ok) {
                    success = true;
                } else {
                    attempt++;
                    if (attempt < MAX_RETRY_ATTEMPTS) {
                        // Update loading message
                        removeMessage('loading-message');
                        addMessageToChat('system', `Retrying (${attempt}/${MAX_RETRY_ATTEMPTS})`, { loading: true, id: 'loading-message' });
                        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait before retrying
                    }
                }
            } catch (error) {
                console.error(`Attempt ${attempt + 1} failed:`, error);
                attempt++;
                if (attempt < MAX_RETRY_ATTEMPTS) {
                    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait before retrying
                }
            }
        }
        
        // Remove loading message
        removeMessage('loading-message');
        
        if (success) {
            const result = await response.json();
            
            // Add AI response to chat
            addMessageToChat('fridge', result.response);
            
            // Refresh dashboard data to show any updates
            setTimeout(refreshDashboardData, 1000);
        } else {
            // Add error message
            addMessageToChat('system', 'Sorry, I couldn\'t process your request right now. Please try again later.');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        removeMessage('loading-message');
        addMessageToChat('system', 'Sorry, an error occurred while processing your request.');
    } finally {
        // Re-enable input
        isSendingMessage = false;
        sendButton.disabled = false;
        userMessageInput.disabled = false;
        userMessageInput.focus();
    }
}

// Handle connection loss and retries
function handleConnectionLoss() {
    updateApiStatus('offline', 'API: Offline');
    isApiAvailable = false;
    
    // Try to reconnect after a delay
    setTimeout(checkApiStatus, 10000);
}

// Initialize the dashboard when the page loads
window.addEventListener('load', initDashboard);

// Handle offline/online events
window.addEventListener('online', checkApiStatus);
window.addEventListener('offline', () => {
    updateApiStatus('offline', 'Browser Offline');
}); 