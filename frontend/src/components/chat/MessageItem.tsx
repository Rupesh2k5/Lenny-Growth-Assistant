import React, { useState } from 'react';
import { User, Sparkles, BookOpen, Layers, Copy, Check } from 'lucide-react';
import { Message, Citation } from '../../types';

interface MessageItemProps {
  message: Message;
  onCitationClick: (citation: Citation) => void;
  onOpenArtifact: (artifactId: string) => void;
  onGenerateShip30FromMessage: (content: string) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  onCitationClick,
  onOpenArtifact,
  onGenerateShip30FromMessage,
}) => {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === 'assistant';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderFormattedLine = (line: string, lineIndex: number) => {
    // If empty line
    if (!line.trim()) {
      return <div key={lineIndex} className="h-2" />;
    }

    // Headers
    if (line.startsWith('### ')) {
      return (
        <h3 key={lineIndex} className="text-sm font-bold text-gray-200 mt-3 mb-1">
          {renderInlineTokens(line.replace('### ', ''))}
        </h3>
      );
    }
    if (line.startsWith('## ')) {
      return (
        <h2 key={lineIndex} className="text-base font-bold text-gray-200 mt-4 mb-1.5 pb-1 border-b border-[#2A3143]">
          {renderInlineTokens(line.replace('## ', ''))}
        </h2>
      );
    }
    if (line.startsWith('# ')) {
      return (
        <h1 key={lineIndex} className="text-lg font-bold text-gray-200 mt-4 mb-2 pb-1 border-b border-[#2A3143]">
          {renderInlineTokens(line.replace('# ', ''))}
        </h1>
      );
    }

    // Horizontal Rule
    if (line.trim() === '---' || line.trim() === '***') {
      return <hr key={lineIndex} className="my-3 border-[#2A3143]" />;
    }

    // Unordered list items
    if (line.startsWith('- ') || line.startsWith('* ')) {
      return (
        <div key={lineIndex} className="flex items-start gap-2 my-1 pl-2">
          <span className="text-amber-400 text-xs font-bold leading-5">•</span>
          <div className="flex-1 text-sm text-gray-200">
            {renderInlineTokens(line.substring(2))}
          </div>
        </div>
      );
    }

    // Numbered list items (e.g. 1. 2. etc)
    const numMatch = line.match(/^(\d+)\.\s+(.+)$/);
    if (numMatch) {
      return (
        <div key={lineIndex} className="flex items-start gap-2 my-1.5 pl-2">
          <span className="text-amber-400 font-bold text-xs leading-5">{numMatch[1]}.</span>
          <div className="flex-1 text-sm text-gray-200">
            {renderInlineTokens(numMatch[2])}
          </div>
        </div>
      );
    }

    // Standard paragraph line
    return (
      <p key={lineIndex} className="text-sm text-gray-200 leading-relaxed my-1">
        {renderInlineTokens(line)}
      </p>
    );
  };

  const renderInlineTokens = (text: string) => {
    // Split by citation markers [S1], [S2] etc.
    const parts = text.split(/(\[S\d+\])/g);

    return parts.map((part, index) => {
      const match = part.match(/^\[S(\d+)\]$/);
      if (match && message.citations) {
        const citId = `S${match[1]}`;
        const citation = message.citations.find((c) => c.citation_id === citId) || message.citations[0];
        return (
          <button
            key={index}
            onClick={() => citation && onCitationClick(citation)}
            className="inline-flex items-center mx-1 px-1.5 py-0.2 rounded text-[11px] font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30 hover:bg-amber-500/25 transition-all cursor-pointer select-none align-baseline"
            title={`Verified Evidence: ${citation?.speaker || 'Lenny Transcript'}`}
          >
            {part}
          </button>
        );
      }

      // Handle bold formatting (**text**)
      if (part.includes('**')) {
        const boldSubparts = part.split(/(\*\*.*?\*\*)/g);
        return (
          <span key={index}>
            {boldSubparts.map((sub, sIdx) => {
              if (sub.startsWith('**') && sub.endsWith('**')) {
                return (
                  <strong key={sIdx} className="font-semibold text-white">
                    {sub.slice(2, -2)}
                  </strong>
                );
              }
              return sub;
            })}
          </span>
        );
      }

      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div
      className={`py-5 px-4 md:px-6 transition-colors ${
        isAssistant ? 'bg-[#10131C]/60 border-y border-[#1A1F2C]/60' : 'bg-transparent'
      }`}
    >
      <div className="max-w-3xl mx-auto flex gap-4">
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center font-bold text-xs shadow-md ${
            isAssistant
              ? 'bg-gradient-to-br from-amber-400 to-amber-600 text-[#10131C]'
              : 'bg-[#2A3143] text-gray-200'
          }`}
        >
          {isAssistant ? <Sparkles className="w-4 h-4" /> : <User className="w-4 h-4" />}
        </div>

        {/* Message Body */}
        <div className="flex-1 space-y-3 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-200">
              {isAssistant ? 'Lenny Growth Assistant' : 'You'}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="p-1 rounded text-[#64748B] hover:text-gray-200 hover:bg-[#1C2230] transition-colors"
                title="Copy message"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          <div className="space-y-1">
            {message.content.split('\n').map((line, idx) => renderFormattedLine(line, idx))}
          </div>

          {/* Sources Footnote Chips */}
          {isAssistant && message.citations && message.citations.length > 0 && (
            <div className="pt-2 border-t border-[#1E2433] flex flex-wrap items-center gap-2">
              <span className="text-[11px] font-semibold text-[#64748B] flex items-center gap-1">
                <BookOpen className="w-3 h-3 text-amber-400" />
                Verified Sources:
              </span>
              {message.citations.map((cit, idx) => (
                <button
                  key={idx}
                  onClick={() => onCitationClick(cit)}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs bg-[#161B26] hover:bg-[#1E2536] border border-[#2A3143] text-gray-300 transition-all hover:border-amber-500/40 cursor-pointer"
                >
                  <span className="text-amber-400 font-bold text-[10px]">
                    [{cit.citation_id || `S${idx + 1}`}]
                  </span>
                  <span className="truncate max-w-[160px] text-[11px] font-medium">
                    {cit.speaker}
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* Attached Artifact Alert Banner */}
          {isAssistant && message.metadata?.artifact_id && (
            <div className="mt-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-semibold text-amber-300">
                  Interactive Strategy Artifact Generated
                </span>
              </div>
              <button
                onClick={() => onOpenArtifact(message.metadata!.artifact_id!)}
                className="px-3 py-1 rounded text-xs font-semibold bg-amber-500 text-gray-200 hover:bg-amber-400 transition-all cursor-pointer"
              >
                View Artifact
              </button>
            </div>
          )}

          {/* Action Chips */}
          {isAssistant && (
            <div className="flex items-center gap-2 pt-1">
              <button
                onClick={() => onGenerateShip30FromMessage(message.content)}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] text-[#94A3B8] hover:text-amber-400 hover:bg-[#161B26] border border-transparent hover:border-amber-500/20 transition-all cursor-pointer"
              >
                <Layers className="w-3 h-3 text-amber-400" />
                Turn into Ship 30 Essay
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
