import { useCallback, useEffect, useState } from "react";
import { fetchArticles } from "../api/client";
import type { Article } from "../types";

export function useArticles(sourceId?: number) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchArticles(sourceId, "completed");
      setArticles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load articles");
    } finally {
      setLoading(false);
    }
  }, [sourceId]);

  useEffect(() => {
    load();
  }, [load]);

  return { articles, loading, error, reload: load };
}
