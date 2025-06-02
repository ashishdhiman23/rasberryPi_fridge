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

// New elements for user management
const usernameSelect = document.getElementById('username-select');
const newUsernameInput = document.getElementById('new-username');
const addUserBtn = document.getElementById('add-user-btn');
const userInfo = document.getElementById('user-info');
const currentUserSpan = document.getElementById('current-user');
const itemCountSpan = document.getElementById('item-count');
const refreshItemsBtn = document.getElementById('refresh-items');
const addItemBtn = document.getElementById('add-item-btn');
const addItemModal = document.getElementById('add-item-modal');
const addItemForm = document.getElementById('add-item-form');
const cancelAddItemBtn = document.getElementById('cancel-add-item');

// Global state
let isApiAvailable = false;
let lastUploadData = null;
let isSendingMessage = false;
let currentUsername = '';
let userItems = [];

// Initialize the dashboard
function initDashboard() {
    // Set up event listeners
    sendButton.addEventListener('click', sendMessage);
    userMessageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // User management event listeners
    usernameSelect.addEventListener('change', handleUserChange);
    addUserBtn.addEventListener('click', toggleAddUserMode);
    refreshItemsBtn.addEventListener('click', refreshUserItems);
    addItemBtn.addEventListener('click', showAddItemModal);
    cancelAddItemBtn.addEventListener('click', hideAddItemModal);
    addItemForm.addEventListener('submit', handleAddItem);

    // Close modal when clicking outside
    addItemModal.addEventListener('click', (e) => {
        if (e.target === addItemModal) {
            hideAddItemModal();
        }
    });

    // Check API status immediately
    checkApiStatus();

    // Set up regular data refresh
    setInterval(refreshDashboardData, REFRESH_INTERVAL);
    
    // Initial data load
    refreshDashboardData();
}

// Handle user selection change
function handleUserChange() {
    const selectedUser = usernameSelect.value;
    if (selectedUser) {
        setCurrentUser(selectedUser);
        refreshUserItems();
    } else {
        clearCurrentUser();
    }
}

// Set the current user
function setCurrentUser(username) {
    currentUsername = username;
    currentUserSpan.textContent = username;
    userInfo.style.display = 'flex';
    
    // Enable/disable action buttons
    refreshItemsBtn.disabled = false;
    addItemBtn.disabled = false;
    
    // Store in localStorage for persistence
    localStorage.setItem('fridgeUsername', username);
}

// Clear the current user
function clearCurrentUser() {
    currentUsername = '';
    currentUserSpan.textContent = 'No user selected';
    itemCountSpan.textContent = '0 items';
    userInfo.style.display = 'none';
    userItems = [];
    
    // Disable action buttons
    refreshItemsBtn.disabled = true;
    addItemBtn.disabled = true;
    
    // Update food items display
    updateFoodItemsDisplay();
    
    // Remove from localStorage
    localStorage.removeItem('fridgeUsername');
}

// Toggle add user mode
function toggleAddUserMode() {
    const isAdding = newUsernameInput.style.display === 'block';
    
    if (isAdding) {
        // Cancel add mode
        newUsernameInput.style.display = 'none';
        newUsernameInput.value = '';
        addUserBtn.textContent = '+ Add User';
    } else {
        // Enter add mode
        newUsernameInput.style.display = 'block';
        newUsernameInput.focus();
        addUserBtn.textContent = 'Cancel';
        
        // Handle enter key in new username input
        newUsernameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                addNewUser();
            }
        });
        
        // Change button behavior
        addUserBtn.onclick = addNewUser;
    }
}

// Add a new user
function addNewUser() {
    const newUsername = newUsernameInput.value.trim();
    if (newUsername) {
        // Check if user already exists
        const existingOptions = Array.from(usernameSelect.options);
        const userExists = existingOptions.some(option => 
            option.value.toLowerCase() === newUsername.toLowerCase()
        );
        
        if (!userExists) {
            // Add new option to select
            const option = document.createElement('option');
            option.value = newUsername;
            option.textContent = newUsername.charAt(0).toUpperCase() + newUsername.slice(1);
            usernameSelect.appendChild(option);
            
            // Select the new user
            usernameSelect.value = newUsername;
            setCurrentUser(newUsername);
            refreshUserItems();
        }
        
        // Reset add mode
        newUsernameInput.style.display = 'none';
        newUsernameInput.value = '';
        addUserBtn.textContent = '+ Add User';
        addUserBtn.onclick = toggleAddUserMode;
    }
}

// Refresh user items from API
async function refreshUserItems() {
    if (!currentUsername) return;
    
    try {
        refreshItemsBtn.disabled = true;
        refreshItemsBtn.textContent = '🔄 Loading...';
        
        const response = await fetch(`${API_URL}/api/user/${currentUsername}/items`);
        
        if (response.ok) {
            userItems = await response.json();
            updateFoodItemsDisplay();
            updateItemCount();
        } else if (response.status === 404) {
            // User not found, but that's okay - they just don't have items yet
            userItems = [];
            updateFoodItemsDisplay();
            updateItemCount();
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('Error refreshing user items:', error);
        showError('Failed to load user items');
    } finally {
        refreshItemsBtn.disabled = false;
        refreshItemsBtn.textContent = '🔄 Refresh';
    }
}

// Update item count display
function updateItemCount() {
    const totalItems = userItems.reduce((sum, item) => sum + item.quantity, 0);
    itemCountSpan.textContent = `${userItems.length} items (${totalItems} total)`;
}

// Update food items display
function updateFoodItemsDisplay() {
    if (!currentUsername) {
        foodItemsContainer.innerHTML = '<div class="no-items">Please select a user to view their items</div>';
        return;
    }
    
    if (userItems.length === 0) {
        foodItemsContainer.innerHTML = '<div class="no-items">No items found. Add some items or scan your fridge!</div>';
        return;
    }
    
    let foodItemsHTML = '';
    userItems.forEach(item => {
        const expiryInfo = getExpiryInfo(item.expiry_date);
        
        foodItemsHTML += `
            <div class="food-item" data-item-id="${item.id}">
                <div class="food-item-main">
                    <span class="food-item-name">${item.name}</span>
                    <span class="food-item-quantity">${item.quantity}</span>
                    ${expiryInfo.html}
                </div>
                <div class="food-item-actions">
                    <button class="edit-btn" onclick="editItem(${item.id})" title="Edit quantity">✏️</button>
                    <button class="delete-btn" onclick="deleteItem(${item.id})" title="Remove item">🗑️</button>
                </div>
            </div>
        `;
    });
    
    foodItemsContainer.innerHTML = foodItemsHTML;
}

// Get expiry information for display
function getExpiryInfo(expiryDate) {
    if (!expiryDate) {
        return { html: '', status: 'none' };
    }
    
    const expiry = new Date(expiryDate);
    const now = new Date();
    const diffTime = expiry - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    let className = 'food-item-expiry';
    let text = '';
    
    if (diffDays < 0) {
        className += ' expired';
        text = `Expired ${Math.abs(diffDays)} days ago`;
    } else if (diffDays === 0) {
        className += ' expires-soon';
        text = 'Expires today';
    } else if (diffDays === 1) {
        className += ' expires-soon';
        text = 'Expires tomorrow';
    } else if (diffDays <= 3) {
        className += ' expires-soon';
        text = `Expires in ${diffDays} days`;
    } else {
        text = `Expires ${expiry.toLocaleDateString()}`;
    }
    
    return {
        html: `<span class="${className}">${text}</span>`,
        status: diffDays < 0 ? 'expired' : diffDays <= 3 ? 'soon' : 'good'
    };
}

// Show add item modal
function showAddItemModal() {
    if (!currentUsername) return;
    
    addItemModal.style.display = 'flex';
    document.getElementById('item-name').focus();
}

// Hide add item modal
function hideAddItemModal() {
    addItemModal.style.display = 'none';
    addItemForm.reset();
}

// Handle add item form submission
async function handleAddItem(e) {
    e.preventDefault();
    
    if (!currentUsername) return;
    
    const itemName = document.getElementById('item-name').value.trim();
    const itemQuantity = parseInt(document.getElementById('item-quantity').value);
    const itemExpiry = document.getElementById('item-expiry').value;
    
    if (!itemName) return;
    
    try {
        const itemData = {
            name: itemName,
            quantity: itemQuantity
        };
        
        if (itemExpiry) {
            itemData.expiry_date = itemExpiry;
        }
        
        const response = await fetch(`${API_URL}/api/user/${currentUsername}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(itemData)
        });
        
        if (response.ok) {
            hideAddItemModal();
            refreshUserItems();
            showSuccess(`Added ${itemName} to your fridge!`);
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('Error adding item:', error);
        showError('Failed to add item');
    }
}

// Edit item quantity (simple prompt for now)
async function editItem(itemId) {
    const item = userItems.find(i => i.id === itemId);
    if (!item) return;
    
    const newQuantity = prompt(`Enter new quantity for ${item.name}:`, item.quantity);
    if (newQuantity === null) return;
    
    const quantity = parseInt(newQuantity);
    if (isNaN(quantity) || quantity < 0) {
        showError('Please enter a valid quantity');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/user/${currentUsername}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: item.name,
                quantity: quantity - item.quantity, // API adds to existing quantity
                expiry_date: item.expiry_date
            })
        });
        
        if (response.ok) {
            refreshUserItems();
            showSuccess(`Updated ${item.name} quantity to ${quantity}`);
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('Error updating item:', error);
        showError('Failed to update item');
    }
}

// Delete item
async function deleteItem(itemId) {
    const item = userItems.find(i => i.id === itemId);
    if (!item) return;
    
    if (!confirm(`Are you sure you want to remove ${item.name} from your fridge?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/user/${currentUsername}/items/${itemId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            refreshUserItems();
            showSuccess(`Removed ${item.name} from your fridge`);
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        showError('Failed to remove item');
    }
}

// Show success message
function showSuccess(message) {
    // Create a temporary success notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        z-index: 1001;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        document.body.removeChild(notification);
    }, 3000);
}

// Show error message
function showError(message) {
    // Create a temporary error notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        z-index: 1001;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        document.body.removeChild(notification);
    }, 5000);
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
            
            // Restore user from localStorage
            const savedUsername = localStorage.getItem('fridgeUsername');
            if (savedUsername) {
                usernameSelect.value = savedUsername;
                setCurrentUser(savedUsername);
                refreshUserItems();
            }
            
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
                // Note: We don't update food items here anymore since they're user-specific
            }
        } catch (error) {
            console.error('Error refreshing dashboard data:', error);
        }
    }
}

// Fetch the last uploaded data
async function fetchLastUploadData() {
    try {
        const response = await fetch(`${API_URL}/api/fridge-status`);
        
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
        timestamp: new Date().toISOString()
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

// Rest of the existing functions (chat functionality, etc.)
function addMessageToChat(type, content, options = {}) {
    const messageId = 'msg-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.id = messageId;
    
    if (options.temp) {
        messageDiv.classList.add('temp-message');
    }
    
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

function removeMessage(id) {
    const message = document.getElementById(id);
    if (message) {
        message.remove();
    }
}

async function sendMessage() {
    const message = userMessageInput.value.trim();
    if (!message || isSendingMessage) return;
    
    isSendingMessage = true;
    
    // Add user message to chat
    addMessageToChat('user', message);
    userMessageInput.value = '';
    
    // Add temporary "thinking" message
    const thinkingId = addMessageToChat('fridge', 'Thinking...', { temp: true });
    
    try {
        // Prepare request
        const requestData = {
            user_message: message,
            session_id: SESSION_ID
        };
        
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        // Remove thinking message
        removeMessage(thinkingId);
        
        if (response.ok) {
            const data = await response.json();
            addMessageToChat('fridge', data.response);
        } else {
            const errorText = await response.text();
            addMessageToChat('fridge', 'Sorry, I encountered an error. Please try again later.');
            console.error('Chat error:', errorText);
        }
    } catch (error) {
        // Remove thinking message
        removeMessage(thinkingId);
        addMessageToChat('fridge', 'Sorry, I\'m having trouble connecting. Please check your internet connection.');
        console.error('Network error:', error);
    } finally {
        isSendingMessage = false;
    }
}

function handleConnectionLoss() {
    updateApiStatus('offline', 'Connection Lost');
    isApiAvailable = false;
}

// Start the dashboard when page loads
document.addEventListener('DOMContentLoaded', initDashboard); 