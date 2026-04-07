import { Link } from "react-router-dom";
import type { Article } from "../types";

export default function ArticleCard({ article }: { article: Article }) {
  return (
    <Link
      to={`/articles/${article.id}`}
      className="block bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow"
    >
      <div className="flex items-center gap-2 mb-2">
        {article.source && (
          <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
            {article.source.name}
          </span>
        )}
        {(article.published_at || article.transformed_at) && (
          <span className="text-xs text-gray-400">
            {new Date(
              article.published_at || article.transformed_at!
            ).toLocaleDateString()}
          </span>
        )}
      </div>
      <h2 className="text-lg font-semibold text-gray-900 mb-2">
        {article.fake_title}
      </h2>
      <p className="text-gray-600 text-sm line-clamp-3">
        {article.fake_description}
      </p>
    </Link>
  );
}
