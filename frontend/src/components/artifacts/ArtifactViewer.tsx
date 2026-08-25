import React, { useState } from 'react';
import { X, Code, Eye, Copy, Download, Check, ShieldCheck, Sparkles } from 'lucide-react';
import { Artifact } from '../../types';
import { SandboxedFrame } from './SandboxedFrame';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifact,
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  if (!isOpen || !artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = artifact.type === 'html' ? 'html' : 'md';
    const blob = new Blob([artifact.content], {
      type: artifact.type === 'html' ? 'text/html' : 'text/markdown',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.toLowerCase().replace(/\s+/g, '-')}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-[520px] border-l border-[#2A3143] bg-[#0E111A] flex flex-col h-[calc(100vh-4rem)] select-none z-20">
      {/* Viewer Header */}
      <div className="h-16 px-5 border-b border-[#2A3143] flex items-center justify-between">
        <div className="flex items-center gap-2 truncate">
          <Sparkles className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <div className="truncate">
            <h3 className="text-sm font-bold text-white truncate">{artifact.title}</h3>
            <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">
              {artifact.type} Artifact • Sandboxed Isolation
            </span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-[#64748B] hover:text-white hover:bg-[#1A202E] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Action Toolbar & Tabs */}
      <div className="px-5 py-2.5 bg-[#131722] border-b border-[#2A3143] flex items-center justify-between">
        {/* Toggle Tabs */}
        <div className="flex items-center gap-1 bg-[#0B0D13] p-1 rounded-lg border border-[#2A3143]">
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-all ${
              activeTab === 'preview'
                ? 'bg-amber-500 text-black shadow-sm'
                : 'text-[#94A3B8] hover:text-white'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            Preview
          </button>

          <button
            onClick={() => setActiveTab('code')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-all ${
              activeTab === 'code'
                ? 'bg-amber-500 text-black shadow-sm'
                : 'text-[#94A3B8] hover:text-white'
            }`}
          >
            <Code className="w-3.5 h-3.5" />
            Raw {artifact.type.toUpperCase()}
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs bg-[#1A202E] hover:bg-[#242B3B] text-gray-200 border border-[#2A3143] transition-colors"
            title="Copy artifact code"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs bg-[#1A202E] hover:bg-[#242B3B] text-gray-200 border border-[#2A3143] transition-colors"
            title="Download file"
          >
            <Download className="w-3 h-3 text-amber-400" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Viewer Content Area */}
      <div className="flex-1 overflow-y-auto p-5 scrollbar-thin">
        {activeTab === 'preview' ? (
          artifact.type === 'html' ? (
            <SandboxedFrame
              htmlContent={artifact.sanitized_content || artifact.content}
              title={artifact.title}
            />
          ) : (
            <div className="p-6 rounded-xl bg-[#131722] border border-[#2A3143] text-sm text-gray-200 whitespace-pre-wrap font-mono leading-relaxed">
              {artifact.content}
            </div>
          )
        ) : (
          <div className="relative">
            <pre className="p-4 rounded-xl bg-[#08090E] border border-[#2A3143] text-xs text-amber-300 font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed">
              {artifact.content}
            </pre>
          </div>
        )}
      </div>

      {/* Security Status Bar */}
      <div className="px-5 py-2 bg-[#0B0D13] border-t border-[#2A3143] flex items-center justify-between text-[11px] text-[#64748B]">
        <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          Isolated CSP Sandbox Active
        </span>
        <span>Render Latency: &lt; 20ms</span>
      </div>
    </div>
  );
};
