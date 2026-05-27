/**
 * Route protection component.
 *
 * Wraps routes that require authentication. If the user is not logged in,
 * they get redirected to the login page. If a specific role is required
 * and the user doesn't have it, they see an access denied message.
 */

import { Navigate } from "react-router-dom";
import useAuthStore from "../store/useAuthStore";

function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return (
      <div className="access-denied">
        <h2>Access Denied</h2>
        <p>You do not have permission to view this page.</p>
      </div>
    );
  }

  return children;
}

export default ProtectedRoute;
