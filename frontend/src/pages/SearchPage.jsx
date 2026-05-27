/**
 * Search page.
 * Users enter natural language queries and get semantically relevant
 * document chunks back, ranked by relevance score.
 */

import { useState } from "react";
import api from "../api/axios";

function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const response = await api.get("/search", {
        params: { q: query, top_k: 5 },
      });
      setResults(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Search failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const getRelevanceColor = (score) => {
    if (score >= 0.7) return "relevance-high";
    if (score >= 0.4) return "relevance-medium";
    return "relevance-low";
  };

  const getRelevanceWidth = (score) => {
    return `${Math.max(score * 100, 5)}%`;
  };

  return (
    <div className="search-page">
      <div className="page-header">
        <h1>Knowledge Search</h1>
        <p className="page-subtitle">
          Ask questions in natural language. The AI will find the most relevant
          information from the knowledge base.
        </p>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., How do I handle customer complaints?"
            autoFocus
          />
          <button
            type="submit"
            className="btn btn-primary search-btn"
            disabled={loading || !query.trim()}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </form>

      {error && <div className="error-message">{error}</div>}

      {results && (
        <div className="search-results">
          <div className="results-header">
            <h2>Results for "{results.query}"</h2>
            <span className="results-count">
              {results.total_results} result{results.total_results !== 1 ? "s" : ""} found
            </span>
          </div>

          {results.results.length === 0 ? (
            <div className="empty-state">
              <h3>No results found</h3>
              <p>
                Try rephrasing your query or upload more documents to the
                knowledge base.
              </p>
            </div>
          ) : (
            <div className="results-list">
              {results.results.map((result, idx) => (
                <div key={idx} className="result-card">
                  <div className="result-header">
                    <span className="result-rank">#{idx + 1}</span>
                    <span className="result-source">
                      {result.document_name}
                    </span>
                    <span className="result-chunk">
                      Chunk {result.chunk_index + 1}
                    </span>
                  </div>

                  <div className="result-text">{result.text}</div>

                  <div className="result-relevance">
                    <span className="relevance-label">Relevance:</span>
                    <div className="relevance-bar">
                      <div
                        className={`relevance-fill ${getRelevanceColor(result.relevance_score)}`}
                        style={{ width: getRelevanceWidth(result.relevance_score) }}
                      ></div>
                    </div>
                    <span className="relevance-score">
                      {(result.relevance_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SearchPage;
