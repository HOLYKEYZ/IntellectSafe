import React from 'react';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
  const navigate = useNavigate();

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

        <form onSubmit={(e) => { e.preventDefault(); navigate('/dashboard'); }} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
             <div>
                <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">First Name</label>
                <input className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors"/>
             </div>
             <div>
                <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Last Name</label>
                <input className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors"/>
             </div>
             <div>
                <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Organization (Optional)</label>
                <input className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors" placeholder="Company Ltd."/>
             </div>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Email</label>
            <input type="email" className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors" placeholder="name@company.com"/>
          </div>
          <div>
             <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-gray-500">Password</label>
             <input type="password" className="w-full bg-[#F5F5F5] border-b-2 border-gray-200 p-4 focus:outline-none focus:border-black transition-colors"/>
          </div>

          <button 
            type="submit"
            className="w-full bg-black text-white py-4 text-sm font-bold tracking-widest hover:bg-gray-800 transition-colors uppercase"
          >
            Submit Request
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
