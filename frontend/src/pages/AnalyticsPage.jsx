/**
 * Analytics page (Admin only).
 * Displays system-wide metrics including task distribution,
 * search query trends, and knowledge base size.
 */

import { useState, useEffect } from "react";
import api from "../api/axios";

function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get("/analytics");
      setAnalytics(response.data);
    } catch (err) {
      console.error("Failed to load analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page-loading">Loading analytics...</div>;
  }

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1>System Analytics</h1>
        <p className="page-subtitle">Detailed metrics for the entire platform.</p>
      </div>

      {analytics && (
        <>
          <div className="analytics-grid">
            {/* Task Overview */}
            <div className="card analytics-card">
              <h3>Task Distribution</h3>
              <div className="stat-group">
                <div className="stat-row">
                  <span>Total Tasks</span>
                  <strong>{analytics.tasks.total}</strong>
                </div>
                <div className="stat-row">
                  <span className="text-pending">Pending</span>
                  <strong>{analytics.tasks.pending}</strong>
                </div>
                <div className="stat-row">
                  <span className="text-progress">In Progress</span>
                  <strong>{analytics.tasks.in_progress}</strong>
                </div>
                <div className="stat-row">
                  <span className="text-completed">Completed</span>
                  <strong>{analytics.tasks.completed}</strong>
                </div>
              </div>
              <div className="completion-rate">
                <div className="rate-circle">
                  <span>{analytics.tasks.completion_rate}%</span>
                </div>
                <p>Overall Completion Rate</p>
              </div>
            </div>

            {/* Knowledge Base Overview */}
            <div className="card analytics-card">
              <h3>Knowledge Base</h3>
              <div className="stat-group">
                <div className="stat-row">
                  <span>Total Documents</span>
                  <strong>{analytics.documents.total}</strong>
                </div>
                <div className="stat-row">
                  <span>Indexed Chunks</span>
                  <strong>{analytics.documents.total_chunks}</strong>
                </div>
              </div>
              <div className="kb-info">
                <p>
                  Documents are split into smaller chunks (avg 500 chars) for
                  better semantic search accuracy.
                </p>
              </div>
            </div>

            {/* Search Analytics */}
            <div className="card analytics-card full-width">
              <h3>Search Activity</h3>
              <div className="stat-group search-stats">
                <div className="stat-item">
                  <span className="stat-value">{analytics.search.total_searches}</span>
                  <span className="stat-label">Total Searches</span>
                </div>
              </div>

              {analytics.search.top_queries.length > 0 ? (
                <div className="top-queries-table">
                  <h4>Top Search Queries</h4>
                  <table>
                    <thead>
                      <tr>
                        <th>Query</th>
                        <th>Searches</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analytics.search.top_queries.map((q, idx) => (
                        <tr key={idx}>
                          <td>{q.query}</td>
                          <td>
                            <div className="query-count-bar" style={{
                              background: `linear-gradient(90deg, var(--primary-light) ${Math.max((q.count / analytics.search.top_queries[0].count) * 100, 5)}%, transparent 0)`
                            }}>
                              {q.count}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="empty-text">No search data available yet.</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default AnalyticsPage;
