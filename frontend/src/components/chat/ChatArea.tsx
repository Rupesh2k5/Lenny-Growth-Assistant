import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, StopCircle } from 'lucide-react';
import { Message, Citation } from '../../types';
import { MessageItem } from './MessageItem';
import { PromptSuggestions } from './PromptSuggestions';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  loadingStage: string | null;
  onSendMessage: (text: string) => void;
  onStopGeneration?: () => void;
  onCitationClick: (citation: Citation) => void;
  onOpenArtifact: (artifactId: string) => void;
  onGenerateShip30: (content: string) => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  loadingStage,
  onSendMessage,
  onStopGeneration,
  onCitationClick,
  onOpenArtifact,
  onGenerateShip30,
}) => {
  const [inputText, setInputText] = useState('');
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isAutoScrollEnabled) {
      scrollToBottom();
    }
  }, [messages, isLoading, loadingStage, isAutoScrollEnabled]);

  const handleScroll = () => {
    if (!chatContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setIsAutoScrollEnabled(isAtBottom);
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText.trim());
    setInputText('');
    setIsAutoScrollEnabled(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full relative overflow-hidden bg-[#0B0D13]">
      <div 
        ref={chatContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto scrollbar-thin pb-48"
      >
        {messages.length === 0 ? (
          <PromptSuggestions onSelectPrompt={(prompt) => onSendMessage(prompt)} />
        ) : (
          <div className="pt-8">
            {messages.map((msg) => (
              <MessageItem
                key={msg.id}
                message={msg}
                onCitationClick={onCitationClick}
                onOpenArtifact={onOpenArtifact}
                onGenerateShip30FromMessage={onGenerateShip30}
              />
            ))}

            {isLoading && (
              <div className="py-5 px-4 md:px-6 bg-[#10131C]/60 border-y border-[#1A1F2C]/60">
                <div className="max-w-3xl mx-auto flex gap-4 items-center">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
                    <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />
                  </div>
                  <div className="space-y-1">
                    <div className="text-xs font-semibold text-amber-400 flex items-center gap-2">
                      <span>{loadingStage || 'Processing...'}</span>
                      <span className="flex gap-0.5">
                        <span className="w-1 h-1 rounded-full bg-amber-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1 h-1 rounded-full bg-amber-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-1 h-1 rounded-full bg-amber-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[#0B0D13] via-[#0B0D13] to-transparent pointer-events-none">
        <div className="max-w-3xl mx-auto pointer-events-auto">
          <form
            onSubmit={handleSubmit}
            className="relative rounded-2xl bg-[#131722] border border-[#2A3143] shadow-2xl focus-within:border-amber-500/50 transition-all"
          >
            <textarea
              ref={inputRef}
              rows={2}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a product or growth question from Lenny's guests..."
              className="w-full pl-4 pr-14 pt-3.5 pb-2 rounded-2xl bg-transparent text-sm text-gray-100 placeholder-[#64748B] focus:outline-none resize-none scrollbar-none"
            />

            {isLoading ? (
              <button
                type="button"
                onClick={onStopGeneration}
                className="absolute right-3 bottom-3 p-2 rounded-xl text-red-500 font-bold hover:bg-red-500/20 transition-all cursor-pointer"
                title="Stop Generating"
              >
                <StopCircle className="w-5 h-5" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!inputText.trim()}
                className={`absolute right-3 bottom-3 p-2 rounded-xl text-black font-bold transition-all ${
                  inputText.trim()
                    ? 'bg-amber-400 hover:bg-amber-300 shadow-md shadow-amber-500/20 cursor-pointer'
                    : 'bg-[#242B3B] text-[#64748B] cursor-not-allowed'
                }`}
              >
                <Send className="w-4 h-4" />
              </button>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};
