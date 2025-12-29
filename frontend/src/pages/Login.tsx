import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // For prototype, just redirect
    navigate('/dashboard');
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

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors"
              placeholder="analyst@aisafety.com"
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
            />
          </div>

          <button 
            type="submit"
            className="w-full bg-black text-white py-4 text-sm font-bold tracking-widest hover:bg-gray-800 transition-colors uppercase"
          >
            Authenticate
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
