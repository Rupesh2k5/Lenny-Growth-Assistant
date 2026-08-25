export interface Citation {
  citation_id: string;
  source_id: string;
  episode_id: string;
  speaker: string;
  title: string;
  url?: string;
  relevance_score: number;
  passage_quote: string;
  content?: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  created_at?: string;
  metadata?: {
    intent?: string;
    provider?: string;
    latency_ms?: number;
    artifact_id?: string;
  };
}

export interface Session {
  id: string;
  title: string;
  created_at?: string;
  updated_at?: string;
  message_count?: number;
  metadata?: Record<string, any>;
}

export interface Artifact {
  id: string;
  session_id: string;
  message_id?: string;
  title: string;
  type: 'markdown' | 'html';
  content: string;
  sanitized_content?: string;
  created_at?: string;
  metadata?: Record<string, any>;
}

export interface Source {
  id: string;
  episode_id: string;
  title: string;
  speaker: string;
  url?: string;
  topics?: string;
  chunk_count?: number;
}

export interface ProviderStatus {
  is_active: boolean;
  status: string;
  model?: string;
  message?: string;
  base_url?: string;
  available_models?: string[];
}

export interface LLMHealthStatus {
  active_provider: string;
  providers: Record<string, ProviderStatus>;
}
