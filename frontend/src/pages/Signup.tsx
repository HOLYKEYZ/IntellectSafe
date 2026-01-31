import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signup, login } from '@/lib/api';

const Signup = () => {
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const fullName = `${firstName} ${lastName}`.trim() || undefined;
      await signup({ email, password, full_name: fullName });
      
      // Auto-login after signup
      const loginResponse = await login({ username: email, password });
      localStorage.setItem('auth_token', loginResponse.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#FDFDFD] text-[#1A1A1A] font-sans">
      <div className="w-full max-w-md p-8">
        <div className="mb-12 text-center">
             <div className="uppercase tracking-[0.2em] text-xs font-bold text-gray-400 mb-4">
              New Application
            </div>
            <h1 className="text-4xl font-serif font-medium mb-2">Join Protocol</h1>
            <p className="text-gray-500">Request clearance for the safety dashboard.</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSignup} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
             <div>
                <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">First Name</label>
                <input 
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors"
                />
             </div>
             <div>
                <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Last Name</label>
                <input 
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors"
                />
             </div>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors" 
              placeholder="name@company.com"
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
               required
               minLength={6}
             />
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full bg-black text-white py-4 text-sm font-bold tracking-widest hover:bg-gray-800 transition-colors uppercase disabled:opacity-50"
          >
            {loading ? 'Creating Account...' : 'Submit Request'}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-gray-500">
           Already verified? <button onClick={() => navigate('/login')} className="text-black font-bold underline">Login</button>
        </div>
      </div>
    </div>
  );
};

export default Signup;
