/**
 * Main layout component with sidebar navigation.
 *
 * This wraps all authenticated pages. The sidebar shows different
 * navigation items depending on whether the user is an Admin or User.
 */

import { NavLink, Outlet, useNavigate } from "react-router-dom";
import useAuthStore from "../../store/useAuthStore";
import {
  HiOutlineHome,
  HiOutlineClipboardList,
  HiOutlineDocumentText,
  HiOutlineSearch,
  HiOutlineChartBar,
  HiOutlineLogout,
} from "react-icons/hi";

function Layout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isAdmin = user?.role === "Admin";

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-logo">TaskFlow</h1>
          <span className="sidebar-subtitle">AI Knowledge System</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" end className="nav-link">
            <HiOutlineHome className="nav-icon" />
            <span>Dashboard</span>
          </NavLink>

          <NavLink to="/tasks" className="nav-link">
            <HiOutlineClipboardList className="nav-icon" />
            <span>Tasks</span>
          </NavLink>

          {isAdmin && (
            <NavLink to="/documents" className="nav-link">
              <HiOutlineDocumentText className="nav-icon" />
              <span>Documents</span>
            </NavLink>
          )}

          <NavLink to="/search" className="nav-link">
            <HiOutlineSearch className="nav-icon" />
            <span>Search</span>
          </NavLink>

          {isAdmin && (
            <NavLink to="/analytics" className="nav-link">
              <HiOutlineChartBar className="nav-icon" />
              <span>Analytics</span>
            </NavLink>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">
              {user?.name?.charAt(0).toUpperCase()}
            </div>
            <div className="user-details">
              <span className="user-name">{user?.name}</span>
              <span className="user-role">{user?.role}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <HiOutlineLogout className="nav-icon" />
            <span>Log out</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
