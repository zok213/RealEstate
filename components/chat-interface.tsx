"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, X, Sparkles, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  onClose?: () => void;
  projectId?: string;
  initialPrompts?: string[];
  className?: string;
}

export function ChatInterface({ 
  onClose, 
  projectId, 
  initialPrompts = [
    "Generate a layout with 50 plots optimized for industrial use",
    "Show me the compliance report for IEAT standards",
    "What's the optimal plot size for this site?",
    "Analyze the DXF file and suggest improvements"
  ],
  className 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your AI design assistant. I can help you analyze DXF files, generate layouts, check compliance, and optimize your industrial park design. How can I help you today?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/design-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [
            ...messages.map(m => ({
              role: m.role,
              parts: [{ type: 'text', text: m.content }]
            })),
            {
              role: 'user',
              parts: [{ type: 'text', text: input }]
            }
          ],
          projectId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || data.message || 'Sorry, I could not process your request.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptClick = (prompt: string) => {
    setInput(prompt);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={cn(
      "flex flex-col h-full bg-[#0a140e] border border-[#1c3326] rounded-lg overflow-hidden",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#1c3326] bg-[#122018]">
        <div className="flex items-center gap-3">
          <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-sm">AI Design Assistant</h3>
            <p className="text-[#95c6a9] text-xs">Powered by Gemini</p>
          </div>
        </div>
        {onClose && (
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onClose}
            className="text-white/70 hover:text-white hover:bg-[#1c3326]"
          >
            <X className="w-5 h-5" />
          </Button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-3 animate-in fade-in-50 duration-300",
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            {message.role === 'assistant' && (
              <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-primary" />
              </div>
            )}
            <div
              className={cn(
                "max-w-[80%] rounded-lg px-4 py-2.5",
                message.role === 'user'
                  ? 'bg-primary text-[#0a130e] ml-auto'
                  : 'bg-[#122018] text-white border border-[#1c3326]'
              )}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <span className={cn(
                "text-xs mt-1 block",
                message.role === 'user' ? 'text-[#0a130e]/70' : 'text-[#95c6a9]'
              )}>
                {message.timestamp.toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </span>
            </div>
            {message.role === 'user' && (
              <div className="size-8 rounded-full bg-[#122018] border border-[#1c3326] flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 animate-in fade-in-50">
            <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary" />
            </div>
            <div className="bg-[#122018] border border-[#1c3326] rounded-lg px-4 py-3">
              <Loader2 className="w-5 h-5 text-primary animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Sample Prompts */}
      {messages.length <= 1 && (
        <div className="px-4 pb-3">
          <p className="text-[#95c6a9] text-xs mb-2">Try these prompts:</p>
          <div className="grid grid-cols-1 gap-2">
            {initialPrompts.slice(0, 3).map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handlePromptClick(prompt)}
                className="text-left text-xs bg-[#122018] border border-[#1c3326] rounded px-3 py-2 text-white/80 hover:text-white hover:border-primary transition-all"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 border-t border-[#1c3326] bg-[#122018]">
        <div className="flex gap-2">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about your design..."
            className="min-h-[44px] max-h-[120px] bg-[#0a140e] border-[#1c3326] text-white placeholder:text-[#95c6a9] resize-none"
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            className="bg-primary hover:bg-[#2dc46b] text-[#0a130e] self-end"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
