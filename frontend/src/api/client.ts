import type {
  Article,
  ChatMessage,
  ChatResponse,
  ScrapeResponse,
  Source,
} from "../types";

const BASE_URL = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export function fetchArticles(
  sourceId?: number,
  status?: string,
  page = 1
): Promise<Article[]> {
  const params = new URLSearchParams();
  if (sourceId) params.set("source_id", String(sourceId));
  if (status) params.set("status", status);
  params.set("page", String(page));
  return request<Article[]>(`/articles?${params}`);
}

export function fetchArticle(id: number): Promise<Article> {
  return request<Article>(`/articles/${id}`);
}

export function fetchSources(): Promise<Source[]> {
  return request<Source[]>("/sources");
}

export function triggerScrape(): Promise<ScrapeResponse> {
  return request<ScrapeResponse>("/scrape", { method: "POST" });
}

export function fetchChatHistory(articleId: number): Promise<ChatMessage[]> {
  return request<ChatMessage[]>(`/articles/${articleId}/chat`);
}

export function sendChatMessage(
  articleId: number,
  message: string
): Promise<ChatResponse> {
  return request<ChatResponse>(`/articles/${articleId}/chat`, {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}
