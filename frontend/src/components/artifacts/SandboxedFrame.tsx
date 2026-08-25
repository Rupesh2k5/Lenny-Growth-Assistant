import React, { useRef, useEffect } from 'react';

interface SandboxedFrameProps {
  htmlContent: string;
  title?: string;
}

export const SandboxedFrame: React.FC<SandboxedFrameProps> = ({ htmlContent, title }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (iframeRef.current) {
      // Create isolated sandboxed document srcdoc
      iframeRef.current.srcdoc = htmlContent;
    }
  }, [htmlContent]);

  return (
    <div className="w-full h-full rounded-xl overflow-hidden bg-white border border-[#2A3143]">
      <iframe
        ref={iframeRef}
        title={title || "Isolated Strategy Artifact"}
        sandbox="allow-scripts"
        referrerPolicy="no-referrer"
        className="w-full h-full min-h-[450px] border-0"
      />
    </div>
  );
};
