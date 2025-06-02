import React, { useState, useRef, useEffect } from 'react';

/**
 * ChatInterface component for the Smart Fridge Dashboard
 * Allows users to ask questions about their fridge contents
 */
const ChatInterface = ({ fridgeData, currentUser }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: currentUser 
        ? `Hello ${currentUser}! I'm your Smart Fridge Assistant. Ask me anything about your fridge contents!`
        : 'Hello! I\'m your Smart Fridge Assistant. Select a user to get personalized responses about your fridge!'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Update welcome message when user changes
  useEffect(() => {
    const welcomeMessage = currentUser 
      ? `Hello ${currentUser}! I'm your Smart Fridge Assistant. Ask me anything about your fridge contents!`
      : 'Hello! I\'m your Smart Fridge Assistant. Select a user to get personalized responses about your fridge!';
    
    setMessages([{ role: 'assistant', content: welcomeMessage }]);
  }, [currentUser]);

  // Auto-scroll to the bottom of the chat when new messages are added
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Check if user is selected
    if (!currentUser) {
      setMessages(prev => [...prev, 
        { role: 'user', content: inputValue },
        { role: 'assistant', content: 'Please select a user first to get personalized responses about their fridge items!' }
      ]);
      setInputValue('');
      return;
    }

    // Add the user message to the chat
    const userMessage = { role: 'user', content: inputValue };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send the message to the backend
      const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: inputValue,
          username: currentUser, // Include current user
          session_id: localStorage.getItem(`chatSessionId_${currentUser}`) || crypto.randomUUID()
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      
      // Save the session ID for future messages (per user)
      if (!localStorage.getItem(`chatSessionId_${currentUser}`)) {
        localStorage.setItem(`chatSessionId_${currentUser}`, data.session_id || crypto.randomUUID());
      }

      // Add the assistant's response to the chat
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        { 
          role: 'assistant', 
          content: 'Sorry, I had trouble processing your request. Please try again later.' 
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 h-[500px] flex flex-col">
      {/* User indicator */}
      {currentUser && (
        <div className="mb-3 px-3 py-2 bg-blue-50 rounded-lg text-sm text-blue-700">
          <span className="font-medium">Chatting as:</span> {currentUser}
        </div>
      )}
      
      <div className="flex-1 overflow-y-auto mb-4 px-2">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-3 ${
              message.role === 'user' ? 'text-right' : 'text-left'
            }`}
          >
            <div
              className={`inline-block px-4 py-2 rounded-lg max-w-[80%] ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="text-left mb-3">
            <div className="inline-block px-4 py-2 rounded-lg bg-gray-100 text-gray-800">
              <div className="flex space-x-1">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef}></div>
      </div>

      <form onSubmit={handleSendMessage} className="flex items-center">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={currentUser ? "Ask about your fridge..." : "Select a user first..."}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          disabled={isLoading || !inputValue.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface; 