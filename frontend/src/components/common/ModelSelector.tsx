import React from 'react';
import { X, Cpu, Check, AlertCircle, Sparkles, RefreshCw } from 'lucide-react';
import { LLMHealthStatus } from '../../types';

interface ModelSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  llmStatus: LLMHealthStatus | null;
  activeProvider: string;
  onSelectProvider: (provider: string) => void;
  onRefresh: () => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  isOpen,
  onClose,
  llmStatus,
  activeProvider,
  onSelectProvider,
  onRefresh,
}) => {
  if (!isOpen) return null;

  const providerConfigs = [
    {
      id: 'ollama',
      name: 'Local Ollama (Mandatory Demo Provider)',
      model: llmStatus?.providers?.ollama?.model || 'llama3.1:8b',
      desc: 'Runs local open-weights inference on your workstation with zero cloud dependencies.',
      type: 'Local Inference',
    },
    {
      id: 'anthropic',
      name: 'Anthropic Claude 3.5 Sonnet',
      model: 'claude-3-5-sonnet-20241022',
      desc: 'Cloud high-reasoning model for complex synthesis, long memos, and nuanced PM analysis.',
      type: 'Cloud API',
    },
    {
      id: 'openai',
      name: 'OpenAI GPT-4o',
      model: 'gpt-4o',
      desc: 'High-throughput multimodal cloud model for low-latency completions and tools.',
      type: 'Cloud API',
    },
    {
      id: 'mock',
      name: 'Deterministic Offline Engine',
      model: 'mock-offline:lenny',
      desc: 'Zero-config local fallback engine ensuring 100% functionality during offline evaluations.',
      type: 'Offline Fallback',
    },
  ];

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#10141F] border border-[#2A3143] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#2A3143] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">LLM Provider & Runtime Switcher</h3>
              <p className="text-xs text-[#94A3B8]">Hot-swap between Local Ollama and Cloud Models</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onRefresh}
              className="p-1.5 rounded-lg text-[#64748B] hover:text-white hover:bg-[#1A202E]"
              title="Refresh provider status"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#64748B] hover:text-white hover:bg-[#1A202E]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Provider Cards */}
        <div className="p-6 space-y-3">
          {providerConfigs.map((prov) => {
            const isSelected = activeProvider === prov.id;
            const provStatus = llmStatus?.providers?.[prov.id];
            const isReady = provStatus?.status === 'ready' || provStatus?.status === 'healthy';

            return (
              <div
                key={prov.id}
                onClick={() => {
                  onSelectProvider(prov.id);
                  onClose();
                }}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#181E2C] border-amber-500/50 shadow-md shadow-amber-500/10'
                    : 'bg-[#131722] border-[#2A3143] hover:border-[#3A435A]'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        isReady ? 'bg-emerald-400' : 'bg-amber-400'
                      }`}
                    />
                    <h4 className="text-xs font-bold text-gray-100">{prov.name}</h4>
                    <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-[#1C2230] text-[#94A3B8] border border-[#2A3143]">
                      {prov.type}
                    </span>
                  </div>

                  {isSelected && (
                    <span className="flex items-center gap-1 text-[11px] font-bold text-amber-400">
                      <Check className="w-3.5 h-3.5" />
                      Active
                    </span>
                  )}
                </div>

                <p className="text-xs text-[#94A3B8] mt-2 leading-relaxed">{prov.desc}</p>
                <div className="mt-2 flex items-center justify-between text-[11px]">
                  <span className="font-mono text-gray-400">Model: {prov.model}</span>
                  <span className="text-[#64748B]">
                    Status: {provStatus?.status || (prov.id === 'mock' ? 'ready' : 'available')}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Advice */}
        <div className="px-6 py-3 bg-[#0B0D13] border-t border-[#2A3143] text-center text-xs text-[#64748B]">
          Switching models takes effect immediately for the next message without restart.
        </div>
      </div>
    </div>
  );
};
