import { useCallback, useEffect, useState } from "react";
import { fetchChatHistory, sendChatMessage } from "../api/client";
import type { ChatMessage } from "../types";

export function useChat(articleId: number) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchChatHistory(articleId)
      .then(setMessages)
      .catch(() => setError("Failed to load chat history"));
  }, [articleId]);

  const send = useCallback(
    async (text: string) => {
      setSending(true);
      setError(null);

      const userMsg: ChatMessage = {
        id: Date.now(),
        article_id: articleId,
        role: "user",
        content: text,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      try {
        const response = await sendChatMessage(articleId, text);
        const assistantMsg: ChatMessage = {
          id: Date.now() + 1,
          article_id: articleId,
          role: "assistant",
          content: response.content,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message");
      } finally {
        setSending(false);
      }
    },
    [articleId]
  );

  return { messages, sending, error, send };
}
