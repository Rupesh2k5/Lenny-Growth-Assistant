import React, { useState, useEffect, useRef } from "react";
import { Header } from "./components/layout/Header";
import { Sidebar } from "./components/layout/Sidebar";
import { ChatArea } from "./components/chat/ChatArea";
import { SourceDrawer } from "./components/chat/SourceDrawer";
import { ArtifactViewer } from "./components/artifacts/ArtifactViewer";
import { Ship30Modal } from "./components/skills/Ship30Modal";
import { ModelSelector } from "./components/common/ModelSelector";
import { api } from "./services/api";
import { Session, Message, Citation, Artifact, LLMHealthStatus } from "./types";

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeProvider, setActiveProvider] = useState<string>("ollama");
  const [llmStatus, setLlmStatus] = useState<LLMHealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingSessionId, setLoadingSessionId] = useState<string | null>(null);
  const [loadingStage, setLoadingStage] = useState<string | null>(null);
  const pollingRef = useRef<boolean>(false);
  const [isSourceDrawerOpen, setIsSourceDrawerOpen] = useState<boolean>(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [allCitations, setAllCitations] = useState<Citation[]>([]);
  const [isArtifactViewerOpen, setIsArtifactViewerOpen] = useState<boolean>(false);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [isShip30ModalOpen, setIsShip30ModalOpen] = useState<boolean>(false);
  const [ship30DefaultTopic, setShip30DefaultTopic] = useState<string>("");
  const [isModelSelectorOpen, setIsModelSelectorOpen] = useState<boolean>(false);

  useEffect(() => {
    loadInitialData();
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  const loadInitialData = async () => {
    try {
      const [fetchedSessions, fetchedLlm] = await Promise.all([api.listSessions(), api.getLLMStatus()]);
      setSessions(fetchedSessions);
      setLlmStatus(fetchedLlm);
      if (fetchedLlm.active_provider) setActiveProvider(fetchedLlm.active_provider);
      if (fetchedSessions.length > 0) {
        await selectSession(fetchedSessions[0].id, true);
      } else {
        createNewSession();
      }
    } catch (e) {
      console.error("Initial data load failed:", e);
      setActiveSessionId("demo-session-pmf-engine");
    }
  };

  const refreshLLMStatus = async () => {
    try { setLlmStatus(await api.getLLMStatus()); } catch (e) { console.error(e); }
  };

  const selectSession = async (sessionId: string, force = false) => {
    if (sessionId === activeSessionId && !force) return;
    setActiveSessionId(sessionId);
    try {
      const msgs = await api.getSessionMessages(sessionId);
      setMessages(msgs);
      setAllCitations(msgs.flatMap((m) => m.citations || []));
      const lastArt = [...msgs].reverse().find((m) => m.metadata?.artifact_id);
      if (lastArt?.metadata?.artifact_id) {
        try {
          const art = await api.getArtifact(lastArt.metadata.artifact_id);
          setActiveArtifact(art);
          setIsArtifactViewerOpen(true);
        } catch (_) { setIsArtifactViewerOpen(false); }
      } else {
        setIsArtifactViewerOpen(false);
      }
      // Resume polling if last message is still generating
      const lastMsg = msgs[msgs.length - 1];
      if (lastMsg?.role === "assistant" && lastMsg.metadata?.status === "generating") {
        setIsLoading(true);
        setLoadingSessionId(sessionId);
        setLoadingStage("Resuming generation...");
        pollUntilComplete(lastMsg.id, sessionId);
      }
    } catch (e) {
      console.error("Failed to load session messages:", e);
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
    } catch (e) { console.error("Failed to create session:", e); }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        const remaining = sessions.filter((s) => s.id !== sessionId);
        remaining.length > 0 ? selectSession(remaining[0].id) : createNewSession();
      }
    } catch (e) { console.error("Failed to delete session:", e); }
  };

  const handleSendMessage = async (text: string) => {
    if (!activeSessionId || isLoading) return;
    const sessionIdAtStart = activeSessionId;
    const tempUserId = `temp-user-${Date.now()}`;
    const tempAsstId = `temp-asst-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      { id: tempUserId, session_id: sessionIdAtStart, role: "user", content: text, created_at: new Date().toISOString() },
      { id: tempAsstId, session_id: sessionIdAtStart, role: "assistant", content: "", created_at: new Date().toISOString() },
    ]);
    setIsLoading(true);
    setLoadingSessionId(sessionIdAtStart);
    setLoadingStage("Sending message...");
    try {
      const queued = await api.queueMessage({ sessionId: sessionIdAtStart, message: text, provider: activeProvider });
      setMessages((prev) => prev.map((m) => {
        if (m.id === tempUserId) return { ...m, id: queued.user_message_id };
        if (m.id === tempAsstId) return { ...m, id: queued.assistant_message_id, metadata: { status: "generating" } };
        return m;
      }));
      setLoadingStage("Generating response...");
      await pollUntilComplete(queued.assistant_message_id, sessionIdAtStart);
    } catch (e) {
      console.error("Send message error:", e);
      setMessages((prev) => prev.filter((m) => m.id !== tempAsstId && m.id !== tempUserId));
      setMessages((prev) => [...prev, {
        id: `err-${Date.now()}`, session_id: sessionIdAtStart, role: "assistant",
        content: "Failed to send. Check your connection and try again.", created_at: new Date().toISOString(),
      }]);
      setIsLoading(false);
      setLoadingSessionId(null);
      setLoadingStage(null);
    }
  };

  // Polls /chat/status/{id} frequently to stream in tokens
  const pollUntilComplete = async (messageId: string, sessionId: string) => {
    pollingRef.current = true;
    const MAX_POLLS = 600; // 5 minutes at 500ms per poll
    let polls = 0;

    const poll = async (): Promise<void> => {
      if (!pollingRef.current || polls >= MAX_POLLS) {
        setIsLoading(false);
        setLoadingSessionId(null);
        setLoadingStage(null);
        return;
      }
      polls++;

      try {
        const status = await api.pollMessageStatus(messageId);

        // Update the UI with the real-time stream content immediately
        setMessages((prev) => prev.map((m) =>
          m.id === messageId
            ? { ...m, content: status.content || m.content, citations: status.citations || [], metadata: status.metadata || {} }
            : m
        ));

        if (status.status === 'generating') {
          // Keep polling every 500ms to get the next chunk of tokens
          if (polls < 6) setLoadingStage('Searching Lenny transcript repository...');
          else if (polls < 12) setLoadingStage('Synthesizing insights from transcripts...');
          else setLoadingStage('Generating grounded response...');
          
          await new Promise((r) => setTimeout(r, 500));
          return poll();
        }

        // --- Complete or Error ---
        
        // Open artifact viewer if artifact was generated
        if (status.metadata?.artifact_id) {
          try {
            const art = await api.getArtifact(status.metadata.artifact_id);
            setActiveArtifact(art);
            setIsArtifactViewerOpen(true);
          } catch (e) { console.error(e); }
        }

        if (status.citations?.length > 0) {
          setAllCitations((prev) => [...prev, ...status.citations]);
        }

        // Refresh session title in sidebar
        const updatedSessions = await api.listSessions();
        setSessions(updatedSessions);

        setIsLoading(false);
        setLoadingSessionId(null);
        setLoadingStage(null);
        pollingRef.current = false;

        if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
          new Notification('Lenny Growth Assistant', { body: 'Your response is ready!', icon: '/vite.svg' });
        }
      } catch (e: any) {
        // If the message is explicitly not found (e.g. deleted), stop polling immediately
        if (e.message && e.message.includes('404')) {
          setIsLoading(false);
          setLoadingSessionId(null);
          setLoadingStage(null);
          pollingRef.current = false;
          
          setMessages((prev) => prev.map((m) =>
            m.id === messageId
              ? { ...m, content: "⚠️ Generation failed: Message was deleted or lost.", metadata: { status: 'error' } }
              : m
          ));
          return;
        }

        // Network hiccup — retry after 1s
        await new Promise((r) => setTimeout(r, 1000));
        return poll();
      }
    };

    return poll();
  };

  const handleStopGeneration = () => {
    pollingRef.current = false;
    setIsLoading(false); setLoadingSessionId(null); setLoadingStage(null);
  };

  const handleGenerateShip30 = async (topic: string, length: number) => {
    if (!activeSessionId) return;
    const sessionIdAtStart = activeSessionId;
    setMessages((prev) => [...prev, {
      id: `msg-${Date.now()}`, session_id: sessionIdAtStart, role: "user",
      content: `Write a Ship 30 for 30 essay about: ${topic}`, created_at: new Date().toISOString(),
    }]);
    setIsLoading(true); setLoadingSessionId(sessionIdAtStart);
    setLoadingStage(`Generating ~${length} word Ship 30 for 30 essay...`);
    try {
      const art = await api.generateShip30Essay({ sessionId: sessionIdAtStart, topic, targetLength: length, provider: activeProvider });
      setActiveArtifact(art); setIsArtifactViewerOpen(true);
      const freshMsgs = await api.getSessionMessages(sessionIdAtStart);
      const msgsWithArt = freshMsgs.map((m, idx) => {
        if (m.role === "assistant" && idx === freshMsgs.length - 1 && !m.metadata?.artifact_id) {
          return { ...m, metadata: { ...m.metadata, artifact_id: art.id } };
        }
        return m;
      });
      setMessages(msgsWithArt);
      setSessions(await api.listSessions());
    } catch (e) {
      console.error("Ship 30 generation error:", e);
      setMessages((prev) => [...prev, {
        id: `err-${Date.now()}`, session_id: sessionIdAtStart, role: "assistant",
        content: "Essay generation failed. Please try again.", created_at: new Date().toISOString(),
      }]);
    } finally {
      setIsLoading(false); setLoadingSessionId(null); setLoadingStage(null);
      if (document.hidden && "Notification" in window && Notification.permission === "granted") {
        new Notification("Lenny Growth Assistant", { body: "Your Ship 30 essay is ready!", icon: "/vite.svg" });
      }
    }
  };

  const handleCitationClick = (citation: Citation) => { setSelectedCitation(citation); setIsSourceDrawerOpen(true); };
  const handleOpenArtifact = async (artifactId: string) => {
    try { const art = await api.getArtifact(artifactId); setActiveArtifact(art); setIsArtifactViewerOpen(true); }
    catch (e) { console.error("Failed to open artifact:", e); }
  };
  const handleOpenShip30WithContext = (content: string) => {
    setShip30DefaultTopic(content.replace(/[#*`[\]]/g, "").slice(0, 100));
    setIsShip30ModalOpen(true);
  };

  const currentSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0B0D13] font-sans text-gray-100">
      <Header
        currentSessionTitle={currentSession?.title || "Intelligence Workspace"}
        llmStatus={llmStatus}
        activeProvider={activeProvider}
        onOpenModelSelector={() => setIsModelSelectorOpen(true)}
        onOpenSourcesList={() => { setSelectedCitation(null); setIsSourceDrawerOpen(true); }}
        onOpenShip30Modal={() => { setShip30DefaultTopic(""); setIsShip30ModalOpen(true); }}
      />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          isLoading={isLoading && loadingSessionId === activeSessionId}
          onSelectSession={selectSession}
          onNewSession={createNewSession}
          onDeleteSession={deleteSession}
          onOpenShip30Modal={() => { setShip30DefaultTopic(""); setIsShip30ModalOpen(true); }}
          onOpenSourcesList={() => { setSelectedCitation(null); setIsSourceDrawerOpen(true); }}
        />
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
        <ArtifactViewer artifact={activeArtifact} isOpen={isArtifactViewerOpen} onClose={() => setIsArtifactViewerOpen(false)} />
      </div>
      <SourceDrawer isOpen={isSourceDrawerOpen} onClose={() => setIsSourceDrawerOpen(false)} citations={allCitations} selectedCitation={selectedCitation} />
      <Ship30Modal
        isOpen={isShip30ModalOpen}
        onClose={() => setIsShip30ModalOpen(false)}
        onGenerate={(topic, length) => { setIsShip30ModalOpen(false); handleGenerateShip30(topic, length); }}
        defaultTopic={ship30DefaultTopic}
      />
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
