import { useState } from "react";
import { triggerScrape } from "../api/client";
import { useArticles } from "../hooks/useArticles";
import ArticleCard from "./ArticleCard";
import SourceFilter from "./SourceFilter";

export default function NewsFeed() {
  const [sourceId, setSourceId] = useState<number | undefined>();
  const { articles, loading, error, reload } = useArticles(sourceId);
  const [scraping, setScraping] = useState(false);
  const [scrapeResult, setScrapeResult] = useState<string | null>(null);

  const handleScrape = async () => {
    setScraping(true);
    setScrapeResult(null);
    try {
      const result = await triggerScrape();
      setScrapeResult(
        `Scraped ${result.articles_scraped} articles, ${result.jobs_enqueued} queued for transformation`
      );
      // Reload after a delay to allow transforms to complete
      setTimeout(reload, 5000);
    } catch {
      setScrapeResult("Failed to scrape articles");
    } finally {
      setScraping(false);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <SourceFilter selected={sourceId} onSelect={setSourceId} />
        <div className="flex gap-3 items-center">
          <button
            onClick={reload}
            className="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Refresh
          </button>
          <button
            onClick={handleScrape}
            disabled={scraping}
            className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {scraping ? "Scraping..." : "Scrape New Articles"}
          </button>
        </div>
      </div>

      {scrapeResult && (
        <div className="mb-4 p-3 bg-green-50 text-green-800 text-sm rounded-lg border border-green-200">
          {scrapeResult}
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg">{error}</div>
      )}

      {loading ? (
        <div className="text-center py-12 text-gray-500">
          Loading articles...
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">No articles yet</p>
          <p className="text-sm">
            Click "Scrape New Articles" to fetch and transform news
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {articles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}
    </div>
  );
}
