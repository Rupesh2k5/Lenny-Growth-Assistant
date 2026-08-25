import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { ChatArea } from './components/chat/ChatArea';
import { SourceDrawer } from './components/chat/SourceDrawer';
import { ArtifactViewer } from './components/artifacts/ArtifactViewer';
import { Ship30Modal } from './components/skills/Ship30Modal';
import { ModelSelector } from './components/common/ModelSelector';
import { api } from './services/api';
import { Session, Message, Citation, Artifact, LLMHealthStatus, Source } from './types';

export const App: React.FC = () => {
  // State
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeProvider, setActiveProvider] = useState<string>('ollama');
  const [llmStatus, setLlmStatus] = useState<LLMHealthStatus | null>(null);

  // Loaders & Progressive Stages
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingSessionId, setLoadingSessionId] = useState<string | null>(null);
  const [loadingStage, setLoadingStage] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Drawers & Modals
  const [isSourceDrawerOpen, setIsSourceDrawerOpen] = useState<boolean>(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [allCitations, setAllCitations] = useState<Citation[]>([]);

  const [isArtifactViewerOpen, setIsArtifactViewerOpen] = useState<boolean>(false);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);

  const [isShip30ModalOpen, setIsShip30ModalOpen] = useState<boolean>(false);
  const [ship30DefaultTopic, setShip30DefaultTopic] = useState<string>('');

  const [isModelSelectorOpen, setIsModelSelectorOpen] = useState<boolean>(false);

  // 1. Initial Load: Fetch Sessions & LLM Health
  useEffect(() => {
    loadInitialData();
    if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }
  }, []);

  const loadInitialData = async () => {
    try {
      const [fetchedSessions, fetchedLlm] = await Promise.all([
        api.listSessions(),
        api.getLLMStatus(),
      ]);
      setSessions(fetchedSessions);
      setLlmStatus(fetchedLlm);
      if (fetchedLlm.active_provider) {
        setActiveProvider(fetchedLlm.active_provider);
      }

      if (fetchedSessions.length > 0) {
        selectSession(fetchedSessions[0].id);
      } else {
        createNewSession();
      }
    } catch (e) {
      console.error('Initial data load failed:', e);
      const defaultId = 'demo-session-pmf-engine';
      setActiveSessionId(defaultId);
    }
  };

  const refreshLLMStatus = async () => {
    try {
      const status = await api.getLLMStatus();
      setLlmStatus(status);
    } catch (e) {
      console.error('Failed to refresh LLM status:', e);
    }
  };

  // 2. Session Management
  const selectSession = async (sessionId: string) => {
    if (sessionId === activeSessionId) return;
    setActiveSessionId(sessionId);
    try {
      const msgs = await api.getSessionMessages(sessionId);
      setMessages(msgs);

      // Extract all citations in session
      const citations = msgs.flatMap((m) => m.citations || []);
      setAllCitations(citations);

      // Check if last message has artifact
      const lastMsgWithArt = [...msgs].reverse().find((m) => m.metadata?.artifact_id);
      if (lastMsgWithArt && lastMsgWithArt.metadata?.artifact_id) {
        const art = await api.getArtifact(lastMsgWithArt.metadata.artifact_id);
        setActiveArtifact(art);
        setIsArtifactViewerOpen(true);
      } else {
        setIsArtifactViewerOpen(false);
      }
    } catch (e) {
      console.error('Failed to load session messages:', e);
    }
  };

  const createNewSession = async () => {
    try {
      const newSess = await api.createSession();
      setSessions((prev) => [newSess, ...prev]);
      setActiveSessionId(newSess.id);
      setMessages([]);
      setIsArtifactViewerOpen(false);
      setIsSourceDrawerOpen(false);
    } catch (e) {
      console.error('Failed to create session:', e);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        const remaining = sessions.filter((s) => s.id !== sessionId);
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          createNewSession();
        }
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  // 3. Live Streaming Chat Messaging (SSE)
  const handleSendMessage = async (text: string) => {
    if (!activeSessionId || isLoading) return;

    // Optimistically append user message
    const userMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: activeSessionId,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    const streamMsgId = `asst-stream-${Date.now()}`;
    const streamingAssistantMsg: Message = {
      id: streamMsgId,
      session_id: activeSessionId,
      role: 'assistant',
      content: '',
      citations: [],
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg, streamingAssistantMsg]);
    setIsLoading(true);
    setLoadingSessionId(activeSessionId);
    setLoadingStage('Searching Lenny transcript repository...');

    const abortController = new AbortController();
    abortControllerRef.current = abortController;
    let accumulatedContent = '';

    await api.streamMessage({
      sessionId: activeSessionId,
      message: text,
      provider: activeProvider,
      signal: abortController.signal,
      onStageUpdate: (_stage, message) => {
        setLoadingStage(message);
      },
      onToken: (token) => {
        accumulatedContent += token;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === streamMsgId ? { ...msg, content: accumulatedContent } : msg
          )
        );
      },
      onComplete: async (data) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === streamMsgId
              ? {
                  ...msg,
                  id: data.messageId || streamMsgId,
                  content: data.fullContent,
                  citations: data.citations,
                  metadata: {
                    intent: data.intent,
                    artifact_id: data.artifactId,
                  },
                }
              : msg
          )
        );

        if (data.citations && data.citations.length > 0) {
          setAllCitations((prev) => [...prev, ...data.citations]);
        }

        if (data.artifactId) {
          try {
            const art = await api.getArtifact(data.artifactId);
            setActiveArtifact(art);
            setIsArtifactViewerOpen(true);
          } catch (err) {
            console.error('Failed to fetch generated artifact:', err);
          }
        }

        // Refresh session list for title update
        const updatedSessions = await api.listSessions();
        setSessions(updatedSessions);
        setIsLoading(false);
        setLoadingSessionId(null);
        setLoadingStage(null);

        // Fetch latest messages to guarantee consistency if user navigated away and back
        try {
          const freshMsgs = await api.getSessionMessages(params.sessionId);
          // Only update if we are still looking at the same session!
          setMessages((currentMsgs) => {
            // Check if current messages belong to this session
            if (currentMsgs.length > 0 && currentMsgs[0].session_id === params.sessionId) {
              return freshMsgs;
            }
            return currentMsgs;
          });
        } catch (e) {
          console.error(e);
        }

        // Notify user if they are on another tab
        if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
          new Notification('Lenny Growth Assistant', {
            body: 'Your response is ready!',
            icon: '/vite.svg',
          });
        }
      },
      onError: (err) => {
        console.error('Streaming chat error, falling back:', err);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === streamMsgId
              ? {
                  ...msg,
                  content:
                    "### Connection Notice\n\nUnable to reach the active LLM provider. Please check that local Ollama is running or switch to the Deterministic Offline provider in the top-right model switcher.",
                }
              : msg
          )
        );
        setIsLoading(false);
        setLoadingSessionId(null);
        setLoadingStage(null);
      },
    });
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
    setLoadingSessionId(null);
    setLoadingStage(null);
  };

  const handleGenerateShip30 = async (topic: string, length: number) => {
    if (!activeSessionId) return;
    setIsLoading(true);
    setLoadingSessionId(activeSessionId);
    setLoadingStage(`Generating ~${length} word Ship 30 for 30 essay...`);

    try {
      const art = await api.generateShip30Essay({
        sessionId: activeSessionId,
        topic,
        targetLength: length,
        provider: activeProvider,
      });

      setActiveArtifact(art);
      setIsArtifactViewerOpen(true);

      const asstMsg: Message = {
        id: `msg-${Date.now()}`,
        session_id: activeSessionId,
        role: 'assistant',
        content: `I've synthesized your **Ship 30 for 30 essay**: *"${art.title}"* (~${art.metadata?.word_count || length} words).\n\nYou can read, preview, copy, or export the rendered essay in the side Artifact Viewer.`,
        created_at: new Date().toISOString(),
        metadata: { artifact_id: art.id },
      };
      setMessages((prev) => [...prev, asstMsg]);
    } catch (e) {
      console.error('Ship 30 generation error:', e);
    } finally {
      setIsLoading(false);
      setLoadingSessionId(null);
      setLoadingStage(null);

      if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
        new Notification('Lenny Growth Assistant', {
          body: 'Your Ship 30 essay is ready!',
          icon: '/vite.svg',
        });
      }
    }
  };

  const handleCitationClick = (citation: Citation) => {
    setSelectedCitation(citation);
    setIsSourceDrawerOpen(true);
  };

  const handleOpenArtifact = async (artifactId: string) => {
    try {
      const art = await api.getArtifact(artifactId);
      setActiveArtifact(art);
      setIsArtifactViewerOpen(true);
    } catch (e) {
      console.error('Failed to open artifact:', e);
    }
  };

  const handleOpenShip30WithContext = (content: string) => {
    const cleanTopic = content.replace(/[#*`[\]]/g, '').slice(0, 100);
    setShip30DefaultTopic(cleanTopic);
    setIsShip30ModalOpen(true);
  };

  const currentSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0B0D13] font-sans text-gray-100">
      {/* Top Header */}
      <Header
        currentSessionTitle={currentSession?.title || 'Intelligence Workspace'}
        llmStatus={llmStatus}
        activeProvider={activeProvider}
        onOpenModelSelector={() => setIsModelSelectorOpen(true)}
        onOpenSourcesList={() => {
          setSelectedCitation(null);
          setIsSourceDrawerOpen(true);
        }}
        onOpenShip30Modal={() => {
          setShip30DefaultTopic('');
          setIsShip30ModalOpen(true);
        }}
      />

      {/* Main 3-Zone Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          isLoading={isLoading && loadingSessionId === activeSessionId}
          onSelectSession={selectSession}
          onNewSession={createNewSession}
          onDeleteSession={deleteSession}
          onOpenShip30Modal={() => {
            setShip30DefaultTopic('');
            setIsShip30ModalOpen(true);
          }}
          onOpenSourcesList={() => {
            setSelectedCitation(null);
            setIsSourceDrawerOpen(true);
          }}
        />

        {/* Center Chat Area */}
        <ChatArea
          messages={messages}
          isLoading={isLoading && loadingSessionId === activeSessionId}
          loadingStage={loadingStage}
          onSendMessage={handleSendMessage}
          onStopGeneration={handleStopGeneration}
          onCitationClick={handleCitationClick}
          onOpenArtifact={handleOpenArtifact}
          onGenerateShip30={handleOpenShip30WithContext}
        />

        {/* Right Artifact Viewer */}
        <ArtifactViewer
          artifact={activeArtifact}
          isOpen={isArtifactViewerOpen}
          onClose={() => setIsArtifactViewerOpen(false)}
        />
      </div>

      {/* Interactive Sources Drawer */}
      <SourceDrawer
        isOpen={isSourceDrawerOpen}
        onClose={() => setIsSourceDrawerOpen(false)}
        citations={allCitations}
        selectedCitation={selectedCitation}
      />

      {/* Ship 30 for 30 Skill Modal */}
      <Ship30Modal
        isOpen={isShip30ModalOpen}
        onClose={() => setIsShip30ModalOpen(false)}
        onGenerate={handleGenerateShip30}
        defaultTopic={ship30DefaultTopic}
      />

      {/* Model Selector Modal */}
      <ModelSelector
        isOpen={isModelSelectorOpen}
        onClose={() => setIsModelSelectorOpen(false)}
        llmStatus={llmStatus}
        activeProvider={activeProvider}
        onSelectProvider={(p) => setActiveProvider(p)}
        onRefresh={refreshLLMStatus}
      />
    </div>
  );
};

export default App;
