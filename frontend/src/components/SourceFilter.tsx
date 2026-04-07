import { useEffect, useState } from "react";
import { fetchSources } from "../api/client";
import type { Source } from "../types";

interface Props {
  selected: number | undefined;
  onSelect: (sourceId: number | undefined) => void;
}

export default function SourceFilter({ selected, onSelect }: Props) {
  const [sources, setSources] = useState<Source[]>([]);

  useEffect(() => {
    fetchSources().then(setSources).catch(console.error);
  }, []);

  if (sources.length === 0) return null;

  return (
    <div className="flex gap-2 flex-wrap">
      <button
        onClick={() => onSelect(undefined)}
        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
          selected === undefined
            ? "bg-blue-600 text-white"
            : "bg-gray-200 text-gray-700 hover:bg-gray-300"
        }`}
      >
        All
      </button>
      {sources.map((source) => (
        <button
          key={source.id}
          onClick={() => onSelect(source.id)}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            selected === source.id
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          {source.name}
        </button>
      ))}
    </div>
  );
}
