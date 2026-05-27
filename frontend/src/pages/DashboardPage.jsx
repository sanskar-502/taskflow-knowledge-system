/**
 * Dashboard page.
 * Shows a quick overview with analytics cards and recent activity.
 * This is the landing page after login for both roles.
 */

import { useState, useEffect } from "react";
import api from "../api/axios";
import useAuthStore from "../store/useAuthStore";

function DashboardPage() {
  const { user } = useAuthStore();
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
    return <div className="page-loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Welcome back, {user?.name}</h1>
        <p className="page-subtitle">
          Here is an overview of your knowledge management system.
        </p>
      </div>

      {analytics && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{analytics.tasks.total}</div>
              <div className="stat-label">Total Tasks</div>
              <div className="stat-bar">
                <div
                  className="stat-bar-fill"
                  style={{
                    width: `${analytics.tasks.completion_rate}%`,
                  }}
                ></div>
              </div>
              <div className="stat-detail">
                {analytics.tasks.completion_rate}% completed
              </div>
            </div>

            <div className="stat-card stat-card-pending">
              <div className="stat-value">{analytics.tasks.pending}</div>
              <div className="stat-label">Pending</div>
            </div>

            <div className="stat-card stat-card-progress">
              <div className="stat-value">{analytics.tasks.in_progress}</div>
              <div className="stat-label">In Progress</div>
            </div>

            <div className="stat-card stat-card-completed">
              <div className="stat-value">{analytics.tasks.completed}</div>
              <div className="stat-label">Completed</div>
            </div>

            <div className="stat-card">
              <div className="stat-value">{analytics.documents.total}</div>
              <div className="stat-label">Documents</div>
              <div className="stat-detail">
                {analytics.documents.total_chunks} chunks indexed
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-value">
                {analytics.search.total_searches}
              </div>
              <div className="stat-label">Searches</div>
            </div>
          </div>

          <div className="dashboard-sections">
            <div className="dashboard-section">
              <h2>Recent Activity</h2>
              {analytics.recent_activity.length === 0 ? (
                <p className="empty-text">No activity recorded yet.</p>
              ) : (
                <div className="activity-list">
                  {analytics.recent_activity.slice(0, 10).map((item, idx) => (
                    <div key={idx} className="activity-item">
                      <div className={`activity-badge badge-${item.action.toLowerCase()}`}>
                        {item.action.replace("_", " ")}
                      </div>
                      <div className="activity-info">
                        <span className="activity-user">
                          {item.user_name || "System"}
                        </span>
                        <span className="activity-time">
                          {new Date(item.timestamp).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {analytics.search.top_queries.length > 0 && (
              <div className="dashboard-section">
                <h2>Popular Searches</h2>
                <div className="query-list">
                  {analytics.search.top_queries.map((q, idx) => (
                    <div key={idx} className="query-item">
                      <span className="query-text">{q.query}</span>
                      <span className="query-count">{q.count} searches</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default DashboardPage;
