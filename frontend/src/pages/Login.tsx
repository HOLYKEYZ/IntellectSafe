import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '@/lib/api';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login({ username: email, password });
      localStorage.setItem('auth_token', response.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#FDFDFD] text-[#1A1A1A] font-sans">
      <div className="w-full max-w-md p-8">
        <div className="mb-12 text-center">
             <div className="uppercase tracking-[0.2em] text-xs font-bold text-gray-400 mb-4">
              Secure Access
            </div>
            <h1 className="text-4xl font-serif font-medium mb-2">Welcome Back</h1>
            <p className="text-gray-500">Enter your credentials to access the safety protocol.</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors"
              placeholder="analyst@aisafety.com"
              required
            />
          </div>
          
          <div>
             <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Password</label>
             <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors"
              placeholder="••••••••"
              required
            />
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full bg-black text-white py-4 text-sm font-bold tracking-widest hover:bg-gray-800 transition-colors uppercase disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Authenticate'}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-gray-500">
           No account? <button onClick={() => navigate('/signup')} className="text-black font-bold underline">Request Access</button>
        </div>
      </div>
    </div>
  );
};

export default Login;
