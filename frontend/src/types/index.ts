export interface Source {
  id: number;
  name: string;
  rss_url: string;
  created_at: string;
}

export type TransformStatus = "pending" | "processing" | "completed" | "failed";

export interface Article {
  id: number;
  source_id: number;
  original_title: string;
  original_description: string;
  original_url: string;
  published_at: string | null;
  fake_title: string | null;
  fake_description: string | null;
  transform_status: TransformStatus;
  transformed_at: string | null;
  created_at: string;
  updated_at: string;
  source: Source | null;
}

export interface ChatMessage {
  id: number;
  article_id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ScrapeResponse {
  articles_scraped: number;
  jobs_enqueued: number;
}

export interface ChatResponse {
  role: string;
  content: string;
}
