import React, { useState, useRef, useEffect } from 'react';

/**
 * ChatInterface component for the Smart Fridge Dashboard
 * Allows users to ask questions about their fridge contents
 */
const ChatInterface = ({ fridgeData }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Smart Fridge Assistant. Ask me anything about your fridge contents!'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

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

    // Add the user message to the chat
    const userMessage = { role: 'user', content: inputValue };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send the message to the backend
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'https://smart-fridge-backend.onrender.com/api'}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: inputValue,
          session_id: localStorage.getItem('chatSessionId') || crypto.randomUUID()
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      
      // Save the session ID for future messages
      if (!localStorage.getItem('chatSessionId')) {
        localStorage.setItem('chatSessionId', data.session_id || crypto.randomUUID());
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
      <div className="flex-1 overflow-y-auto mb-4 px-2">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-3 ${
              message.role === 'user' ? 'text-right' : 'text-left'
            }`}
          >
            <div
              className={`inline-block px-4 py-2 rounded-lg ${
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
          placeholder="Ask about your fridge..."
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