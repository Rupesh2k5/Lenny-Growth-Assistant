import React, { useState } from 'react';
import { X, Layers, Sparkles, PenTool, CheckCircle2, ArrowRight } from 'lucide-react';

interface Ship30ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (topic: string, length: number) => void;
  defaultTopic?: string;
}

export const Ship30Modal: React.FC<Ship30ModalProps> = ({
  isOpen,
  onClose,
  onGenerate,
  defaultTopic = '',
}) => {
  const [topic, setTopic] = useState(defaultTopic || '');
  const [targetLength, setTargetLength] = useState(1250);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    onGenerate(topic.trim(), targetLength);
    onClose();
  };

  const presetTopics = [
    'The 4-Step Superhuman PMF Engine by Rahul Vohra',
    'Elena Verna’s B2B Growth Loops and PLG vs Free Trial',
    'Brian Chesky on 11-Star Experience Design & Founder Mode',
    'Shreyas Doshi’s LNO Framework for High-Agency Product Leaders',
  ];

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#10141F] border border-[#2A3143] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#2A3143] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Write with Lenny (Ship 30 for 30)</h3>
              <p className="text-xs text-[#94A3B8]">Transform grounded podcast insights into atomic digital essays</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-[#64748B] hover:text-white hover:bg-[#1A202E]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-200 mb-1.5">
              What topic or framework would you like to write about?
            </label>
            <textarea
              rows={3}
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. How to move from linear acquisition funnels to compounding growth loops..."
              className="w-full p-3 rounded-xl bg-[#161B26] border border-[#2A3143] text-sm text-gray-100 placeholder-[#64748B] focus:outline-none focus:border-amber-500/50 resize-none"
              required
            />
          </div>

          {/* Quick Presets */}
          <div>
            <span className="text-[11px] font-semibold text-[#64748B] uppercase tracking-wider block mb-2">
              Popular Framework Presets:
            </span>
            <div className="space-y-1.5">
              {presetTopics.map((pt, idx) => (
                <button
                  type="button"
                  key={idx}
                  onClick={() => setTopic(pt)}
                  className="w-full text-left px-3 py-2 rounded-lg text-xs bg-[#161B26] hover:bg-[#1E2536] border border-[#2A3143] text-[#94A3B8] hover:text-amber-400 transition-colors truncate"
                >
                  • {pt}
                </button>
              ))}
            </div>
          </div>

          {/* Target Length Selector */}
          <div>
            <label className="block text-xs font-semibold text-gray-200 mb-1.5">
              Target Essay Length
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { label: 'Atomic (~500 words)', val: 500 },
                { label: 'Standard (~1,250 words)', val: 1250 },
                { label: 'Deep Dive (~2,000 words)', val: 2000 },
              ].map((opt) => (
                <button
                  type="button"
                  key={opt.val}
                  onClick={() => setTargetLength(opt.val)}
                  className={`py-2 px-2 rounded-lg text-xs font-semibold border text-center transition-all ${
                    targetLength === opt.val
                      ? 'bg-amber-500/20 text-amber-400 border-amber-500/50'
                      : 'bg-[#161B26] text-[#94A3B8] border-[#2A3143] hover:border-[#3A435A]'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="pt-3 flex items-center justify-end gap-2 border-t border-[#2A3143]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-[#94A3B8] hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!topic.trim()}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-amber-500 text-black hover:bg-amber-400 shadow-md shadow-amber-500/20 transition-all cursor-pointer disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Generate Grounded Essay
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
