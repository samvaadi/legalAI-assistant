import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../types/contract';
import { useAppStore } from '../state/store';
import { mockApi } from '../services/mockApi';

const STARTER_PROMPTS = [
  'What are the biggest risks in this contract?',
  'Give me a negotiation strategy',
  'Explain the indemnification clause',
  'What should I push back on?',
];

export const Suggestions: React.FC = () => {
  const { session, activeContractId, addMessage, initSession } = useAppStore();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (activeContractId && !session) {
      initSession(activeContractId);
    }
  }, [activeContractId, session, initSession]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session?.messages]);

  const send = async (text: string) => {
    if (!text.trim() || !activeContractId) return;
    setInput('');

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    addMessage(userMsg);
    setLoading(true);

    try {
      const history = (session?.messages || []).map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const reply = await mockApi.chat(activeContractId, text, history);
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: reply,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  const messages = session?.messages || [];

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="chat-welcome-icon">⚖</div>
            <h3>Legal AI Assistant</h3>
            <p>Ask questions about this contract, get negotiation advice, or request clause rewrites.</p>
            <div className="chat-starters">
              {STARTER_PROMPTS.map((p) => (
                <button key={p} className="starter-chip" onClick={() => send(p)}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatBubble key={msg.id} message={msg} />
          ))
        )}

        {loading && (
          <div className="chat-bubble assistant">
            <div className="bubble-avatar">AI</div>
            <div className="bubble-body thinking">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="chat-input-wrap">
        <input
          className="chat-input"
          placeholder="Ask about any clause, risk, or strategy…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send(input)}
          disabled={loading || !activeContractId}
        />
        <button
          className="chat-send-btn"
          onClick={() => send(input)}
          disabled={loading || !input.trim() || !activeContractId}
        >
          →
        </button>
      </div>
    </div>
  );
};

const ChatBubble: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const isUser = message.role === 'user';
  const time = new Date(message.timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit',
  });

  return (
    <div className={`chat-bubble ${isUser ? 'user' : 'assistant'}`}>
      {!isUser && <div className="bubble-avatar">AI</div>}
      <div className="bubble-content">
        <div className="bubble-body">{message.content}</div>
        <span className="bubble-time">{time}</span>
      </div>
    </div>
  );
};