import React from 'react';
import { Layers, BookOpen, Sparkles } from 'lucide-react';
import { LLMHealthStatus } from '../../types';

interface HeaderProps {
  currentSessionTitle: string;
  llmStatus: LLMHealthStatus | null;
  activeProvider: string;
  onOpenModelSelector: () => void;
  onOpenSourcesList: () => void;
  onOpenShip30Modal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentSessionTitle,
  llmStatus,
  activeProvider,
  onOpenModelSelector,
  onOpenSourcesList,
  onOpenShip30Modal
}) => {
  return (
    <header className="h-16 border-b border-[#2A3143] bg-[#0B0D13] px-6 flex items-center justify-between select-none z-10">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-amber-500 text-black flex items-center justify-center">
          <Sparkles className="w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-bold text-gray-200">Lenny Growth Assistant</h1>
            <span className="text-[9px] font-bold bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded">FDE EDITION</span>
          </div>
          <span className="text-xs text-[#64748B]">{currentSessionTitle}</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={onOpenShip30Modal}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#2A3143] hover:border-amber-500/50 hover:bg-amber-500/10 text-xs font-semibold text-gray-300 hover:text-amber-400 transition-colors"
        >
          <Layers className="w-4 h-4 text-amber-500" />
          Write with Lenny (Ship 30)
        </button>

        <button
          onClick={onOpenSourcesList}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#2A3143] hover:border-blue-500/50 hover:bg-blue-500/10 text-xs font-semibold text-gray-300 hover:text-blue-400 transition-colors"
        >
          <BookOpen className="w-4 h-4 text-blue-500" />
          Knowledge Base (7 Episodes)
        </button>
      </div>
      
      <div className="flex items-center gap-4">
        <button
          onClick={onOpenModelSelector}
          className="flex items-center gap-2 text-xs font-semibold text-[#64748B] hover:text-gray-300 transition-colors"
        >
          <span className="w-2 h-2 rounded-full " />
          {activeProvider === 'ollama' ? 'Ollama (Local)' : activeProvider}
        </button>
      </div>
    </header>
  );
};
