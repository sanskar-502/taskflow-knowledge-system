/**
 * Tasks page.
 * Admin: can create tasks, assign to users, and delete tasks.
 * User: can view assigned tasks and update their status.
 * Both: can filter and sort the task list.
 */

import { useState, useEffect } from "react";
import api from "../api/axios";
import useAuthStore from "../store/useAuthStore";

function TasksPage() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === "Admin";

  const [tasks, setTasks] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [order, setOrder] = useState("desc");

  // Create task form (admin only)
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    assigned_to: "",
    due_date: "",
  });
  const [users, setUsers] = useState([]);
  const [formError, setFormError] = useState("");

  useEffect(() => {
    fetchTasks();
  }, [page, statusFilter, sortBy, order]);

  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
    }
  }, [isAdmin]);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params = { page, limit: 10, sort_by: sortBy, order };
      if (statusFilter) params.status = statusFilter;

      const response = await api.get("/tasks", { params });
      setTasks(response.data.tasks);
      setTotal(response.data.total);
      setTotalPages(response.data.total_pages);
    } catch (err) {
      console.error("Failed to load tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    // We don't have a dedicated users endpoint, so we skip this
    // In a real app you'd have GET /users for admin
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    setFormError("");
    try {
      const payload = {
        title: formData.title,
        description: formData.description || null,
        assigned_to: formData.assigned_to
          ? parseInt(formData.assigned_to)
          : null,
        due_date: formData.due_date || null,
      };
      await api.post("/tasks", payload);
      setShowForm(false);
      setFormData({ title: "", description: "", assigned_to: "", due_date: "" });
      fetchTasks();
    } catch (err) {
      setFormError(err.response?.data?.detail || "Failed to create task");
    }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await api.patch(`/tasks/${taskId}`, { status: newStatus });
      fetchTasks();
    } catch (err) {
      console.error("Failed to update task:", err);
    }
  };

  const handleDelete = async (taskId) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    try {
      await api.delete(`/tasks/${taskId}`);
      fetchTasks();
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case "Pending":
        return "status-pending";
      case "In Progress":
        return "status-progress";
      case "Completed":
        return "status-completed";
      default:
        return "";
    }
  };

  return (
    <div className="tasks-page">
      <div className="page-header">
        <div>
          <h1>Tasks</h1>
          <p className="page-subtitle">{total} tasks total</p>
        </div>
        {isAdmin && (
          <button
            className="btn btn-primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? "Cancel" : "New Task"}
          </button>
        )}
      </div>

      {/* Create task form */}
      {showForm && isAdmin && (
        <div className="card form-card">
          <h3>Create New Task</h3>
          {formError && <div className="error-message">{formError}</div>}
          <form onSubmit={handleCreateTask}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="task-title">Title</label>
                <input
                  id="task-title"
                  type="text"
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                  placeholder="Enter task title"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="task-assigned">Assign to (User ID)</label>
                <input
                  id="task-assigned"
                  type="number"
                  value={formData.assigned_to}
                  onChange={(e) =>
                    setFormData({ ...formData, assigned_to: e.target.value })
                  }
                  placeholder="User ID"
                />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="task-desc">Description</label>
              <textarea
                id="task-desc"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Describe the task"
                rows={3}
              />
            </div>
            <div className="form-group">
              <label htmlFor="task-due">Due Date</label>
              <input
                id="task-due"
                type="date"
                value={formData.due_date}
                onChange={(e) =>
                  setFormData({ ...formData, due_date: e.target.value })
                }
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Create Task
            </button>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All</option>
            <option value="Pending">Pending</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Sort:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="created_at">Created</option>
            <option value="due_date">Due Date</option>
            <option value="title">Title</option>
            <option value="status">Status</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Order:</label>
          <select value={order} onChange={(e) => setOrder(e.target.value)}>
            <option value="desc">Newest first</option>
            <option value="asc">Oldest first</option>
          </select>
        </div>
      </div>

      {/* Task list */}
      {loading ? (
        <div className="page-loading">Loading tasks...</div>
      ) : tasks.length === 0 ? (
        <div className="empty-state">
          <h3>No tasks found</h3>
          <p>
            {statusFilter
              ? "Try changing your filters."
              : "No tasks have been created yet."}
          </p>
        </div>
      ) : (
        <>
          <div className="task-list">
            {tasks.map((task) => (
              <div key={task.id} className="task-card">
                <div className="task-header">
                  <h3 className="task-title">{task.title}</h3>
                  <span className={`status-badge ${getStatusClass(task.status)}`}>
                    {task.status}
                  </span>
                </div>
                {task.description && (
                  <p className="task-description">{task.description}</p>
                )}
                <div className="task-meta">
                  {task.assignee_name && (
                    <span className="meta-item">
                      Assigned to: <strong>{task.assignee_name}</strong>
                    </span>
                  )}
                  {task.due_date && (
                    <span className="meta-item">
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </span>
                  )}
                  <span className="meta-item">
                    Created: {new Date(task.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="task-actions">
                  {/* Status change dropdown */}
                  {(isAdmin || task.assigned_to === user?.id) && (
                    <select
                      className="status-select"
                      value={task.status}
                      onChange={(e) =>
                        handleStatusChange(task.id, e.target.value)
                      }
                    >
                      <option value="Pending">Pending</option>
                      <option value="In Progress">In Progress</option>
                      <option value="Completed">Completed</option>
                    </select>
                  )}
                  {isAdmin && (
                    <button
                      className="btn btn-danger btn-small"
                      onClick={() => handleDelete(task.id)}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-outline"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-outline"
                disabled={page === totalPages}
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default TasksPage;
