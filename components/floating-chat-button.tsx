"use client";

import React, { useState } from 'react';
import { MessageSquare, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatInterface } from '@/components/chat-interface';
import { cn } from '@/lib/utils';

interface FloatingChatButtonProps {
  projectId?: string;
  className?: string;
}

export function FloatingChatButton({ projectId, className }: FloatingChatButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          className={cn(
            "fixed bottom-6 right-6 size-14 rounded-full shadow-[0_0_30px_rgba(54,226,123,0.3)] bg-primary hover:bg-[#2dc46b] text-[#0a130e] z-50 transition-all hover:scale-110",
            className
          )}
          aria-label="Open AI Chat"
        >
          <MessageSquare className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 size-3 bg-[#f97316] rounded-full border-2 border-[#0a130e] animate-pulse" />
        </Button>
      )}

      {/* Chat Sidebar */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 animate-in fade-in-0 duration-200"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Chat Panel */}
          <div className="fixed right-0 top-0 bottom-0 w-full md:w-[480px] z-50 animate-in slide-in-from-right-5 duration-300">
            <ChatInterface 
              onClose={() => setIsOpen(false)} 
              projectId={projectId}
              className="h-full rounded-none md:rounded-l-lg"
            />
          </div>
        </>
      )}
    </>
  );
}
