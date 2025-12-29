import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = () => {
  // In a real app, this would check a token in localStorage or similar
  // For this demo, we'll simulate it or just allow it for now, 
  // BUT the user asked to restrict it.
  // Let's check for a dummy token "auth_token" which we will set on Login.
  const isAuthenticated = localStorage.getItem('auth_token');

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
