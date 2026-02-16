import { Navigate, Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getCurrentUser } from '@/lib/api';

const ProtectedRoute = () => {
  const [status, setStatus] = useState<'loading' | 'authenticated' | 'unauthenticated'>('loading');

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setStatus('unauthenticated');
      return;
    }

    // Validate token with backend
    getCurrentUser()
      .then(() => setStatus('authenticated'))
      .catch(() => {
        localStorage.removeItem('auth_token');
        setStatus('unauthenticated');
      });
  }, []);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-2">
          <div className="w-8 h-8 border-2 border-zinc-900 dark:border-white border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-muted-foreground">Validating session...</p>
        </div>
      </div>
    );
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
