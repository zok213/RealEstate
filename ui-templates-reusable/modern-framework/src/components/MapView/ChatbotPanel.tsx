import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../../services/designApi';
import { ChatMessage } from '../../types';
import './ChatbotPanel.css';

interface ChatbotPanelProps {
  estateId: string;
}

const ChatbotPanel: React.FC<ChatbotPanelProps> = ({ estateId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    'Draw parallel roads with equal spacing',
    'Auto-snap building to grid',
    'Calculate road area coverage',
    'Optimize plot layout',
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Simulate AI response (replace with actual API call)
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I can help you with "${inputText}". Here are some suggestions based on your request.`,
        timestamp: new Date().toISOString(),
        suggestions: [
          'Use primary roads with 25m width',
          'Maintain 30m setback from boundary',
          'Add green buffer zones between plots',
        ],
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputText(suggestion);
  };

  return (
    <div className={`chatbot-panel ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="chatbot-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex items-center gap-2">
          <span className="chatbot-icon">🤖</span>
          <h3 className="chatbot-title">Design Assistant</h3>
          <span className="badge badge-success">Online</span>
        </div>
        <button className="btn-icon btn-secondary">
          {isExpanded ? '▼' : '▲'}
        </button>
      </div>

      {isExpanded && (
        <>
          <div className="chatbot-messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                <p className="welcome-text">
                  👋 Hi! I'm your Design Assistant. I can help you with:
                </p>
                <ul className="welcome-list">
                  <li>Drawing roads and placing buildings</li>
                  <li>Optimizing plot layouts</li>
                  <li>Calculating areas and distances</li>
                  <li>Compliance checking</li>
                </ul>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.role === 'user' ? 'user' : 'assistant'}`}
              >
                <div className="message-content">
                  {message.content}
                </div>
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="message-suggestions">
                    {message.suggestions.map((suggestion, index) => (
                      <div key={index} className="suggestion-chip">
                        💡 {suggestion}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <div className="message-content loading">
                  <span className="loading-dot">●</span>
                  <span className="loading-dot">●</span>
                  <span className="loading-dot">●</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {messages.length === 0 && (
            <div className="quick-suggestions">
              <p className="suggestions-label">Quick Suggestions:</p>
              <div className="suggestions-grid">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion-button"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="chatbot-input">
            <input
              type="text"
              className="input"
              placeholder="How can I help with your design?"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={isLoading}
            />
            <button
              className="btn btn-primary"
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isLoading}
            >
              📤 Send
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ChatbotPanel;
