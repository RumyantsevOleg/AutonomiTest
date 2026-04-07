import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchArticle } from "../api/client";
import type { Article } from "../types";
import ChatPanel from "./ChatPanel";

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [showOriginal, setShowOriginal] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetchArticle(Number(id))
      .then(setArticle)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading...</div>;
  }

  if (!article) {
    return <div className="text-center py-12 text-red-500">Article not found</div>;
  }

  const title = showOriginal ? article.original_title : article.fake_title;
  const description = showOriginal
    ? article.original_description
    : article.fake_description;

  return (
    <div>
      <Link
        to="/"
        className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-6"
      >
        &larr; Back to feed
      </Link>

      <article className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            {article.source && (
              <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                {article.source.name}
              </span>
            )}
            <span
              className={`text-xs px-2 py-0.5 rounded ${
                article.transform_status === "completed"
                  ? "bg-green-50 text-green-700"
                  : article.transform_status === "failed"
                    ? "bg-red-50 text-red-700"
                    : "bg-yellow-50 text-yellow-700"
              }`}
            >
              {article.transform_status}
            </span>
          </div>
          <button
            onClick={() => setShowOriginal(!showOriginal)}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {showOriginal ? "Show Satirical" : "Show Original"}
          </button>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-4">{title}</h1>
        {article.published_at && (
          <p className="text-sm text-gray-400 mb-3">
            Published: {new Date(article.published_at).toLocaleString()}
          </p>
        )}
        <p className="text-gray-700 leading-relaxed whitespace-pre-line">
          {description}
        </p>

        <div className="mt-4 pt-4 border-t border-gray-100">
          <a
            href={article.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:underline"
          >
            View original article &rarr;
          </a>
        </div>
      </article>

      {article.transform_status === "completed" && (
        <ChatPanel articleId={article.id} />
      )}
    </div>
  );
}
