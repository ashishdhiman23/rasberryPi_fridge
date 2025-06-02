import React, { useState } from 'react';

const UserItemsManager = ({
  currentUser,
  onUserChange,
  userItems,
  onRefreshItems,
  onAddItem,
  onDeleteItem,
  loading,
  error
}) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [newUser, setNewUser] = useState('');
  const [showAddUser, setShowAddUser] = useState(false);
  
  // Form state for adding items
  const [itemForm, setItemForm] = useState({
    name: '',
    quantity: 1,
    expiry_date: ''
  });

  // Predefined users (can be extended)
  const predefinedUsers = ['ashish', 'john', 'mary', 'guest'];

  // Handle user selection
  const handleUserSelect = (e) => {
    const username = e.target.value;
    onUserChange(username);
  };

  // Add new user
  const handleAddUser = () => {
    if (newUser.trim()) {
      onUserChange(newUser.trim());
      setNewUser('');
      setShowAddUser(false);
    }
  };

  // Handle form submission for adding items
  const handleAddItem = async (e) => {
    e.preventDefault();
    
    if (!itemForm.name.trim()) return;
    
    const success = await onAddItem({
      name: itemForm.name.trim(),
      quantity: parseInt(itemForm.quantity),
      ...(itemForm.expiry_date && { expiry_date: itemForm.expiry_date })
    });
    
    if (success) {
      setItemForm({ name: '', quantity: 1, expiry_date: '' });
      setShowAddModal(false);
    }
  };

  // Format expiry date for display
  const formatExpiryDate = (expiryDate) => {
    if (!expiryDate) return null;
    
    const expiry = new Date(expiryDate);
    const now = new Date();
    const diffTime = expiry - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    let className = 'text-xs px-2 py-1 rounded-full ';
    let text = '';
    
    if (diffDays < 0) {
      className += 'bg-red-100 text-red-800';
      text = `Expired ${Math.abs(diffDays)} days ago`;
    } else if (diffDays === 0) {
      className += 'bg-orange-100 text-orange-800';
      text = 'Expires today';
    } else if (diffDays === 1) {
      className += 'bg-orange-100 text-orange-800';
      text = 'Expires tomorrow';
    } else if (diffDays <= 3) {
      className += 'bg-yellow-100 text-yellow-800';
      text = `Expires in ${diffDays} days`;
    } else {
      className += 'bg-green-100 text-green-800';
      text = `Expires ${expiry.toLocaleDateString()}`;
    }
    
    return <span className={className}>{text}</span>;
  };

  // Calculate total items
  const totalItems = userItems.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h2 className="text-lg font-semibold text-gray-700">Your Food Items</h2>
        
        {/* User Selection */}
        <div className="flex items-center gap-3">
          <label htmlFor="user-select" className="text-sm font-medium text-gray-600">
            User:
          </label>
          <select
            id="user-select"
            value={currentUser}
            onChange={handleUserSelect}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select User</option>
            {predefinedUsers.map(user => (
              <option key={user} value={user}>
                {user.charAt(0).toUpperCase() + user.slice(1)}
              </option>
            ))}
          </select>
          
          {!showAddUser ? (
            <button
              onClick={() => setShowAddUser(true)}
              className="px-3 py-2 text-sm bg-green-500 text-white rounded-md hover:bg-green-600"
            >
              + Add User
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={newUser}
                onChange={(e) => setNewUser(e.target.value)}
                placeholder="Enter username"
                className="px-2 py-1 text-sm border border-gray-300 rounded"
                onKeyPress={(e) => e.key === 'Enter' && handleAddUser()}
              />
              <button
                onClick={handleAddUser}
                className="px-2 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
              >
                Add
              </button>
              <button
                onClick={() => {setShowAddUser(false); setNewUser('');}}
                className="px-2 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      {/* User Info */}
      {currentUser && (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 p-3 bg-gray-50 rounded-md gap-2">
          <div className="text-sm text-gray-600">
            <span className="font-medium">Current user:</span> {currentUser}
          </div>
          <div className="text-sm text-gray-600">
            <span className="font-medium">Items:</span> {userItems.length} types ({totalItems} total)
          </div>
          <div className="flex gap-2">
            <button
              onClick={onRefreshItems}
              disabled={loading}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? '🔄 Loading...' : '🔄 Refresh'}
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              disabled={!currentUser}
              className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
            >
              + Add Item
            </button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Items Display */}
      <div className="min-h-[200px]">
        {!currentUser ? (
          <div className="flex items-center justify-center h-32 text-gray-500">
            Please select a user to view their items
          </div>
        ) : loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="ml-2 text-gray-600">Loading items...</span>
          </div>
        ) : userItems.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-500">
            No items found. Add some items or scan your fridge!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {userItems.map((item) => (
              <div
                key={item.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900 capitalize">{item.name}</h3>
                  <button
                    onClick={() => onDeleteItem(item.id)}
                    className="text-red-500 hover:text-red-700 text-sm"
                    title="Remove item"
                  >
                    🗑️
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Qty: {item.quantity}
                  </span>
                  {formatExpiryDate(item.expiry_date)}
                </div>
                {item.date_added && (
                  <div className="mt-2 text-xs text-gray-400">
                    Added: {new Date(item.date_added).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Item Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Add New Item</h3>
            <form onSubmit={handleAddItem}>
              <div className="mb-4">
                <label htmlFor="item-name" className="block text-sm font-medium text-gray-700 mb-1">
                  Item Name
                </label>
                <input
                  type="text"
                  id="item-name"
                  value={itemForm.name}
                  onChange={(e) => setItemForm({ ...itemForm, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Apple, Milk, Cheese"
                  required
                />
              </div>
              <div className="mb-4">
                <label htmlFor="item-quantity" className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity
                </label>
                <input
                  type="number"
                  id="item-quantity"
                  value={itemForm.quantity}
                  onChange={(e) => setItemForm({ ...itemForm, quantity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                  required
                />
              </div>
              <div className="mb-6">
                <label htmlFor="item-expiry" className="block text-sm font-medium text-gray-700 mb-1">
                  Expiry Date (optional)
                </label>
                <input
                  type="date"
                  id="item-expiry"
                  value={itemForm.expiry_date}
                  onChange={(e) => setItemForm({ ...itemForm, expiry_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false);
                    setItemForm({ name: '', quantity: 1, expiry_date: '' });
                  }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                >
                  Add Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserItemsManager; 