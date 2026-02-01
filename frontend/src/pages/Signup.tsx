import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signup, login } from '@/lib/api';
import ThemeToggle from '@/components/ThemeToggle';

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
    <div className="min-h-screen flex flex-col bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 font-sans transition-colors">
      {/* Top bar with back button and theme toggle */}
      <div className="flex justify-between p-4">
        <button 
          onClick={() => navigate('/')}
          className="text-sm font-medium text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors flex items-center gap-1"
        >
          ← Back to Home
        </button>
        <ThemeToggle />
      </div>

      <div className="flex-1 flex items-center justify-center">
        <div className="w-full max-w-md p-8">
          <div className="mb-12 text-center">
            <div className="uppercase tracking-[0.2em] text-xs font-bold text-gray-400 dark:text-zinc-500 mb-4">
              New Application
            </div>
            <h1 className="text-4xl font-serif font-medium mb-2">Join Protocol</h1>
            <p className="text-gray-500 dark:text-zinc-400">Request clearance for the safety dashboard.</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-md text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
               <div>
                  <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500 dark:text-zinc-400">First Name</label>
                  <input 
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="w-full bg-zinc-100 dark:bg-zinc-800 border-b-2 border-gray-200 dark:border-zinc-700 p-4 focus:outline-none focus:border-black dark:focus:border-white transition-colors text-zinc-900 dark:text-zinc-100"
                  />
               </div>
               <div>
                  <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500 dark:text-zinc-400">Last Name</label>
                  <input 
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="w-full bg-zinc-100 dark:bg-zinc-800 border-b-2 border-gray-200 dark:border-zinc-700 p-4 focus:outline-none focus:border-black dark:focus:border-white transition-colors text-zinc-900 dark:text-zinc-100"
                  />
               </div>
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500 dark:text-zinc-400">Email</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-zinc-100 dark:bg-zinc-800 border-b-2 border-gray-200 dark:border-zinc-700 p-4 focus:outline-none focus:border-black dark:focus:border-white transition-colors text-zinc-900 dark:text-zinc-100" 
                placeholder="name@company.com"
                required
              />
            </div>
            <div>
               <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500 dark:text-zinc-400">Password</label>
               <input 
                 type="password" 
                 value={password}
                 onChange={(e) => setPassword(e.target.value)}
                 className="w-full bg-zinc-100 dark:bg-zinc-800 border-b-2 border-gray-200 dark:border-zinc-700 p-4 focus:outline-none focus:border-black dark:focus:border-white transition-colors text-zinc-900 dark:text-zinc-100"
                 required
                 minLength={6}
               />
            </div>

            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 py-4 text-sm font-bold tracking-widest hover:bg-zinc-700 dark:hover:bg-zinc-200 transition-colors uppercase disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Submit Request'}
            </button>
          </form>

          <div className="mt-8 text-center text-sm text-gray-500 dark:text-zinc-400">
             Already verified? <button onClick={() => navigate('/login')} className="text-zinc-900 dark:text-white font-bold underline">Login</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
