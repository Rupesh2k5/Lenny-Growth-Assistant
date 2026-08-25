import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, Search, Layers, BookOpen, Loader2 } from 'lucide-react';
import { Session } from '../../types';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  isLoading?: boolean;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  onOpenShip30Modal: () => void;
  onOpenSourcesList: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  isLoading,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onOpenShip30Modal,
  onOpenSourcesList,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <aside className="w-64 border-r border-[#2A3143] flex flex-col h-full bg-[#10131C] select-none">
      <div className="p-4 border-b border-[#2A3143] space-y-4">
        <button
          onClick={onNewSession}
          className="w-full flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-400 text-black px-4 py-2.5 rounded-xl font-bold transition-all shadow-md shadow-amber-500/10"
        >
          <Plus className="w-4 h-4 stroke-[3]" />
          New Conversation
        </button>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
          <input
            type="text"
            placeholder="Search sessions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#1A1F2C] border border-[#2A3143] text-sm text-gray-200 rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:border-amber-500/50 transition-colors placeholder-[#64748B]"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-thin">
        <h3 className="px-3 text-[10px] font-bold text-[#64748B] mb-2 uppercase tracking-wider">
          Recent Conversations
        </h3>
        
        {filteredSessions.map((session) => (
          <div
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={"group flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all "}
          >
            <div className="flex items-center gap-3 overflow-hidden">
              <MessageSquare className={"w-4 h-4 shrink-0 "} />
              <span className={"truncate text-sm font-semibold "}>
                {session.title || 'New Conversation'}
              </span>
              {activeSessionId === session.id && isLoading && (
                <Loader2 className="w-3 h-3 text-amber-500 animate-spin shrink-0" />
              )}
            </div>
            
            {activeSessionId === session.id && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-[#2A3143] rounded-lg text-[#64748B] hover:text-red-400 transition-all"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-[#2A3143] space-y-2">
        <button
          onClick={onOpenShip30Modal}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold text-[#94A3B8] hover:text-white hover:bg-[#1A1F2C] transition-colors"
        >
          <Layers className="w-4 h-4 text-amber-500" />
          Ship 30 Essay Skill
        </button>
        <button
          onClick={onOpenSourcesList}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold text-[#94A3B8] hover:text-white hover:bg-[#1A1F2C] transition-colors"
        >
          <BookOpen className="w-4 h-4 text-blue-500" />
          Transcript Knowledge Base
        </button>
      </div>
    </aside>
  );
};
