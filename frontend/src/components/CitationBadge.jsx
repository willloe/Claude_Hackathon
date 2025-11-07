/**
 * Citation badge component for displaying source references
 */
import React, { useState } from 'react';

const CitationBadge = ({ source, index }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="inline-block">
      <button
        onClick={() => setExpanded(!expanded)}
        className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded-full hover:bg-blue-200 transition-colors"
      >
        <span>📄</span>
        <span>{source.filename}</span>
        <span className="text-blue-600">p.{source.page}</span>
      </button>

      {expanded && (
        <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-lg text-sm">
          <div className="font-semibold text-gray-700 mb-1">
            Source: {source.filename}, Page {source.page}
          </div>
          <div className="text-gray-600 italic">"{source.chunk_text}"</div>
        </div>
      )}
    </div>
  );
};

export default CitationBadge;
