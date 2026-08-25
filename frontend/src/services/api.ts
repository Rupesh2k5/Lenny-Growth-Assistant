import { Session, Message, Artifact, Source, LLMHealthStatus, Citation } from '../types';

const API_BASE = '/api';

export const api = {
  // Health & Providers
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getLLMStatus(): Promise<LLMHealthStatus> {
    const res = await fetch(`${API_BASE}/health/llm`);
    if (!res.ok) throw new Error('Failed to fetch LLM status');
    return res.json();
  },

  // Sessions
  async listSessions(): Promise<Session[]> {
    const res = await fetch(`${API_BASE}/sessions`);
    if (!res.ok) throw new Error('Failed to fetch sessions');
    return res.json();
  },

  async createSession(title?: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title || 'New Conversation' }),
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  async getSessionMessages(sessionId: string): Promise<Message[]> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
    if (!res.ok) throw new Error('Failed to fetch messages');
    const raw: any[] = await res.json();
    // Explicitly map backend `metadata` (which contains artifact_id) to our Message type
    return raw.map((m) => ({
      id: m.id,
      session_id: m.session_id,
      role: m.role,
      content: m.content,
      citations: m.citations || [],
      created_at: m.created_at,
      metadata: m.metadata || {},
    }));
  },

  async deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete session');
  },

  // Chat (Standard REST)
  async sendMessage(params: {
    sessionId: string;
    message: string;
    provider?: string;
  }): Promise<Message> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        message: params.message,
        provider: params.provider,
      }),
    });
    if (!res.ok) throw new Error('Chat request failed');
    const data = await res.json();
    return {
      id: data.message_id,
      session_id: data.session_id,
      role: 'assistant',
      content: data.content,
      citations: data.citations,
      metadata: {
        intent: data.intent,
        provider: data.provider,
        latency_ms: data.latency_ms,
        artifact_id: data.artifact_id,
      },
    };
  },

  // Chat (SSE Live Streaming)
  async streamMessage(params: {
    sessionId: string;
    message: string;
    provider?: string;
    signal?: AbortSignal;
    onStageUpdate: (stage: string, message: string) => void;
    onToken: (token: string) => void;
    onComplete: (data: {
      messageId: string;
      fullContent: string;
      citations: Citation[];
      artifactId?: string;
      intent: string;
    }) => void;
    onError: (error: any) => void;
  }): Promise<void> {
    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: params.signal,
        body: JSON.stringify({
          session_id: params.sessionId,
          message: params.message,
          provider: params.provider,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Streaming failed: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.replace('data: ', ''));
              if (data.stage && data.message) {
                params.onStageUpdate(data.stage, data.message);
              }
              if (data.token) {
                params.onToken(data.token);
              }
              if (data.stage === 'complete') {
                params.onComplete({
                  messageId: data.message_id,
                  fullContent: data.full_content,
                  citations: data.citations || [],
                  artifactId: data.artifact_id,
                  intent: data.intent,
                });
              }
            } catch (err) {
              console.error('Failed to parse SSE line:', err);
            }
          }
        }
      }
    } catch (e) {
      params.onError(e);
    }
  },

  // Skills
  async generateShip30Essay(params: {
    sessionId: string;
    topic: string;
    targetLength?: number;
    provider?: string;
  }): Promise<Artifact> {
    const res = await fetch(`${API_BASE}/skills/ship30`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        topic: params.topic,
        target_length: params.targetLength || 1250,
        provider: params.provider,
      }),
    });
    if (!res.ok) throw new Error('Ship 30 essay generation failed');
    const data = await res.json();
    return {
      id: data.artifact_id,
      session_id: data.session_id,
      title: data.title,
      type: 'markdown',
      content: data.content,
      sanitized_content: data.content,
      metadata: { word_count: data.word_count, model: data.model },
    };
  },

  async generateArtifact(params: {
    sessionId: string;
    prompt: string;
    artifactType?: string;
    provider?: string;
  }): Promise<Artifact> {
    const res = await fetch(`${API_BASE}/skills/artifact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        prompt: params.prompt,
        artifact_type: params.artifactType || 'html',
        provider: params.provider,
      }),
    });
    if (!res.ok) throw new Error('Artifact generation failed');
    const data = await res.json();
    return {
      id: data.artifact_id,
      session_id: data.session_id,
      title: data.title,
      type: data.type,
      content: data.content,
      sanitized_content: data.sanitized_content,
      metadata: { model: data.model },
    };
  },

  // Artifacts
  async getArtifact(artifactId: string): Promise<Artifact> {
    const res = await fetch(`${API_BASE}/artifacts/${artifactId}`);
    if (!res.ok) throw new Error('Failed to fetch artifact');
    return res.json();
  },

  // Sources
  async listSources(): Promise<Source[]> {
    const res = await fetch(`${API_BASE}/sources`);
    if (!res.ok) throw new Error('Failed to fetch sources');
    return res.json();
  },

  async getSourceDetail(sourceId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/sources/${sourceId}`);
    if (!res.ok) throw new Error('Failed to fetch source details');
    return res.json();
  },
};
