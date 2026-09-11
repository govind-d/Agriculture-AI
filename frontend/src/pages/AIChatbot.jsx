import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User } from 'lucide-react';
import api from '../api';

const AIChatbot = () => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your AI agriculture assistant. Ask me anything about farming, crops, diseases, or weather.", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = { id: Date.now(), text: input, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/api/chatbot/message', { message: userMsg.text });
      const botMsg = { id: Date.now() + 1, text: res.data.response, sender: 'bot' };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = { id: Date.now() + 1, text: "Sorry, I'm having trouble connecting right now. Please try again later.", sender: 'bot', error: true };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ padding: '1rem', height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Bot className="logo-icon" /> AI Farm Assistant
      </h2>

      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
        
        {/* Messages Area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', background: 'var(--bg-color)' }}>
          {messages.map((msg) => (
            <div key={msg.id} style={{
              display: 'flex',
              gap: '0.75rem',
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row'
            }}>
              <div style={{ 
                width: '32px', height: '32px', borderRadius: '50%', 
                background: msg.sender === 'user' ? 'var(--primary-200)' : 'var(--primary-500)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                color: msg.sender === 'user' ? 'var(--primary-800)' : 'white'
              }}>
                {msg.sender === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div style={{
                background: msg.sender === 'user' ? 'var(--primary-500)' : msg.error ? 'rgba(239, 68, 68, 0.1)' : 'white',
                color: msg.sender === 'user' ? 'white' : msg.error ? 'var(--accent-red)' : 'var(--text-color)',
                padding: '0.75rem 1rem',
                borderRadius: '1rem',
                borderTopRightRadius: msg.sender === 'user' ? '0' : '1rem',
                borderTopLeftRadius: msg.sender === 'bot' ? '0' : '1rem',
                boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                lineHeight: 1.5,
                whiteSpace: 'pre-wrap',
                fontSize: '0.95rem'
              }}>
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', gap: '0.75rem', alignSelf: 'flex-start', maxWidth: '80%' }}>
              <div style={{ 
                width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary-500)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: 'white'
              }}>
                <Bot size={18} />
              </div>
              <div style={{ background: 'white', padding: '0.75rem 1.5rem', borderRadius: '1rem', borderTopLeftRadius: '0', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', display: 'flex', gap: '0.25rem' }}>
                <span className="dot-typing"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: '1rem', background: 'white', borderTop: '1px solid var(--primary-100)' }}>
          <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="text" 
              className="input-field" 
              style={{ flex: 1 }}
              placeholder="Type your farming question here..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="btn btn-primary" disabled={!input.trim() || loading} style={{ padding: '0 1.5rem' }}>
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
      
      {/* CSS for typing animation */}
      <style>{`
        .dot-typing {
          position: relative;
          width: 6px;
          height: 6px;
          border-radius: 5px;
          background-color: var(--primary-300);
          color: var(--primary-300);
          animation: dot-typing 1s infinite linear;
          margin-left: 10px;
          margin-right: 10px;
        }
        .dot-typing::before, .dot-typing::after {
          content: '';
          display: inline-block;
          position: absolute;
          top: 0;
          width: 6px;
          height: 6px;
          border-radius: 5px;
          background-color: var(--primary-300);
          color: var(--primary-300);
        }
        .dot-typing::before {
          left: -10px;
          animation: dot-typing-before 1s infinite linear;
        }
        .dot-typing::after {
          left: 10px;
          animation: dot-typing-after 1s infinite linear;
        }
        @keyframes dot-typing {
          0% { box-shadow: 0 0 0 0 var(--primary-300); }
          50% { box-shadow: 0 -5px 0 0 var(--primary-300); }
          100% { box-shadow: 0 0 0 0 var(--primary-300); }
        }
        @keyframes dot-typing-before {
          0% { box-shadow: 0 -5px 0 0 var(--primary-300); }
          50% { box-shadow: 0 0 0 0 var(--primary-300); }
          100% { box-shadow: 0 0 0 0 var(--primary-300); }
        }
        @keyframes dot-typing-after {
          0% { box-shadow: 0 0 0 0 var(--primary-300); }
          50% { box-shadow: 0 0 0 0 var(--primary-300); }
          100% { box-shadow: 0 -5px 0 0 var(--primary-300); }
        }
      `}</style>
    </div>
  );
};

export default AIChatbot;
