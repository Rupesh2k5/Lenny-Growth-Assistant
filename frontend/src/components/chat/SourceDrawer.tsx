import React from 'react';
import { X, BookOpen, ExternalLink, Quote, Sparkles } from 'lucide-react';
import { Citation } from '../../types';

interface SourceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  citations: Citation[];
  selectedCitation: Citation | null;
}

export const SourceDrawer: React.FC<SourceDrawerProps> = ({
  isOpen,
  onClose,
  citations,
  selectedCitation,
}) => {
  if (!isOpen) return null;

  const displayList = selectedCitation ? [selectedCitation] : citations;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-[#10141E] border-l border-[#2A3143] shadow-2xl z-40 flex flex-col animate-in slide-in-from-right duration-200">
      {/* Drawer Header */}
      <div className="h-16 px-5 border-b border-[#2A3143] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-bold text-white">Transcript Evidence & Sources</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-[#64748B] hover:text-white hover:bg-[#1A202E] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Drawer Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-thin">
        {displayList.length === 0 ? (
          <div className="text-center py-12 text-xs text-[#64748B]">
            No sources attached to this selection.
          </div>
        ) : (
          displayList.map((cit, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-[#161B26] border border-[#2A3143] space-y-3"
            >
              {/* Header Badges */}
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  [{cit.citation_id || `S${idx + 1}`}]
                </span>
                <span className="text-[10px] text-emerald-400 font-semibold">
                  {Math.round((cit.relevance_score || 0.9) * 100)}% Match
                </span>
              </div>

              {/* Guest & Episode */}
              <div>
                <h4 className="text-xs font-bold text-gray-100">{cit.speaker}</h4>
                <p className="text-[11px] text-[#94A3B8] mt-0.5">{cit.title}</p>
                {cit.episode_id && (
                  <span className="text-[10px] text-[#64748B] block mt-0.5">
                    Episode: {cit.episode_id}
                  </span>
                )}
              </div>

              {/* Passage Quote */}
              <div className="p-3 rounded-lg bg-[#0B0D13] border border-[#1E2433] text-xs text-gray-300 relative">
                <Quote className="w-3.5 h-3.5 text-amber-500/30 absolute top-2 left-2" />
                <p className="pl-4 italic leading-relaxed text-[11px]">
                  "{cit.passage_quote || cit.content}"
                </p>
              </div>

              {/* Podcast URL */}
              {cit.url && (
                <a
                  href={cit.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] text-amber-400 hover:text-amber-300 font-medium transition-colors"
                >
                  <span>Listen on Lenny's Podcast</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
