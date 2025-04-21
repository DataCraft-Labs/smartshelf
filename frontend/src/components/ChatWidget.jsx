import React, { useState, useRef, useEffect } from 'react';
import { chatApi } from '../services/api.js';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      text: "Olá! Eu sou o assistente SmartShelf AI. Posso responder perguntas sobre seu estoque, produtos e recomendações. Como posso ajudar você hoje?", 
      sender: "bot" 
    }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // Transform messages format for API
  const formatMessagesForAPI = (messages) => {
    return messages
      .filter(msg => msg.id !== 1) // Filter out the welcome message
      .map(msg => ({
        role: msg.sender === "user" ? "user" : "assistant",
        content: msg.text
      }));
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (newMessage.trim() === '') return;

    // Add user message
    const userMessage = { id: messages.length + 1, text: newMessage, sender: "user" };
    setMessages([...messages, userMessage]);
    setNewMessage('');
    
    // Show loading indicator
    setIsLoading(true);
    setError(null);

    try {
      // Get conversation history formatted for API
      const history = formatMessagesForAPI(messages);
      
      // Send message to API
      const response = await chatApi.sendMessage(newMessage, history);
      
      // Add bot response
      const botResponse = { 
        id: messages.length + 2, 
        text: response.response, 
        sender: "bot",
        prediction_data: response.prediction_data
      };
      
      setMessages(prevMessages => [...prevMessages, botResponse]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Falha ao comunicar com o assistente. Tente novamente.');
      
      // Add fallback error message
      const errorMessage = { 
        id: messages.length + 2, 
        text: "Desculpe, estou enfrentando problemas para processar sua mensagem. Por favor, tente novamente mais tarde.", 
        sender: "bot",
        isError: true
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Collapsed Chat Bubble */}
      {!isOpen && (
        <div 
          className="fixed bottom-6 right-6 rounded-lg shadow-xl overflow-hidden cursor-pointer z-50 bg-surface hover:bg-surface/90 transition-colors"
          onClick={toggleChat}
        >
          <div className="bg-primary px-4 py-2 text-sm font-medium text-white">
            Assistente de Dados
          </div>
          <div className="flex items-center p-3 gap-2">
            <div className="bg-primary/20 p-1.5 rounded-full">
              <svg className="w-6 h-6 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zm-4 7a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                <path d="M12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" opacity="0.3" />
              </svg>
            </div>
            <span className="text-white font-medium">IA SmartShelf</span>
          </div>
        </div>
      )}

      {/* Expanded Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-80 sm:w-96 rounded-lg shadow-2xl z-50 flex flex-col bg-surface max-h-[600px] border border-gray-700">
          {/* Chat Header */}
          <div className="bg-primary px-4 py-3 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="bg-white/20 p-1 rounded-full">
                <svg className="w-5 h-5 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-4-9h8c.55 0 1 .45 1 1s-.45 1-1 1H8c-.55 0-1-.45-1-1s.45-1 1-1zm0 3h8c.55 0 1 .45 1 1s-.45 1-1 1H8c-.55 0-1-.45-1-1s.45-1 1-1zm0-6h8c.55 0 1 .45 1 1s-.45 1-1 1H8c-.55 0-1-.45-1-1s.45-1 1-1z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white">SmartShelf AI</h3>
            </div>
            <button 
              onClick={toggleChat}
              className="text-white/80 hover:text-white focus:outline-none"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-800/50 min-h-[300px] max-h-[400px]">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.sender === 'bot' && (
                  <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center mr-2">
                    <svg className="w-5 h-5 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" />
                      <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" />
                    </svg>
                  </div>
                )}
                <div 
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.sender === 'user' 
                      ? 'bg-primary text-white rounded-br-none' 
                      : message.isError
                        ? 'bg-red-900/60 text-white rounded-bl-none'
                        : 'bg-gray-700 text-white rounded-bl-none'
                  }`}
                >
                  {message.text}
                </div>
                {message.sender === 'user' && (
                  <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center ml-2">
                    <svg className="w-5 h-5 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0-6c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm0 7c-2.67 0-8 1.34-8 4v3h16v-3c0-2.66-5.33-4-8-4zm6 5H6v-.99c.2-.72 3.3-2.01 6-2.01s5.8 1.29 6 2v1z" />
                    </svg>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center mr-2">
                  <svg className="w-5 h-5 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" />
                    <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" />
                  </svg>
                </div>
                <div className="bg-gray-700 text-white rounded-lg rounded-bl-none px-4 py-2 max-w-[80%]">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            {error && !isLoading && (
              <div className="text-center py-2">
                <p className="text-xs text-red-400">{error}</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-3 border-t border-gray-700 bg-gray-800/70">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Pergunte sobre seu estoque, produtos..."
                className="flex-1 bg-gray-700 border border-gray-600 rounded-full px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary"
                disabled={isLoading}
              />
              <button 
                type="submit"
                className="bg-primary hover:bg-primary-dark text-white rounded-full p-2 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50"
                disabled={newMessage.trim() === '' || isLoading}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
};

export default ChatWidget; 