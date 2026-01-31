import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Book, Code, Terminal } from 'lucide-react';

const Docs = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white text-zinc-900 font-sans">
       <nav className="fixed top-0 w-full px-6 py-4 flex justify-between items-center z-50 bg-white border-b border-zinc-200">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
           <div className="w-8 h-8 flex items-center justify-center">
             <img src="/logo.png" alt="IntellectSafe Logo" className="w-full h-full object-contain filter brightness-0" />
           </div>
           <span className="text-lg font-bold tracking-tight">IntellectSafe Docs</span>
        </div>
        <div className="flex items-center gap-6">
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-sm font-medium hover:text-zinc-600 transition-colors">
            <ArrowLeft className="w-4 h-4" /> Home
          </button>
          <button onClick={() => navigate('/dashboard')} className="text-sm font-medium hover:text-zinc-600 transition-colors">Dashboard</button>
          <a href={`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/docs`} target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:text-zinc-600 transition-colors">API Docs</a>
        </div>
      </nav>


      <div className="flex pt-20 h-screen">
         {/* Sidebar */}
         <aside className="w-64 border-r border-zinc-200 hidden md:block overflow-y-auto p-6 fixed h-full">
            <h3 className="font-bold text-sm uppercase tracking-wider text-zinc-500 mb-6">Getting Started</h3>
            <ul className="space-y-3 text-sm font-medium text-zinc-700">
               <li className="text-zinc-900 font-bold">Introduction</li>
               <li className="hover:text-emerald-600 cursor-pointer">Quick Start</li>
               <li className="hover:text-emerald-600 cursor-pointer">Architecture</li>
            </ul>
            
            <h3 className="font-bold text-sm uppercase tracking-wider text-zinc-500 mt-8 mb-6">API Reference</h3>
            <ul className="space-y-3 text-sm font-medium text-zinc-700">
               <li className="hover:text-emerald-600 cursor-pointer">Scan Endpoints</li>
               <li className="hover:text-emerald-600 cursor-pointer">Auth Tokens</li>
               <li className="hover:text-emerald-600 cursor-pointer">Webhooks</li>
            </ul>
         </aside>

         {/* Content */}
         <main className="flex-1 md:ml-64 p-12 overflow-y-auto">
            <h1 className="text-4xl font-serif font-medium mb-6">Introduction</h1>
            <p className="text-lg text-zinc-600 leading-relaxed mb-8 max-w-3xl">
               IntellectSafe provides a unified security layer for Large Language Models. 
               By sitting between your users and your AI models, we intercept malicious prompts, sanitize inputs, 
               and verify outputs against a council of safety models.
            </p>

            <div className="grid md:grid-cols-2 gap-6 mb-12">
               <div className="border border-zinc-200 p-6 rounded-lg hover:border-black transition-colors cursor-pointer group">
                  <div className="mb-4 text-emerald-600"><Code className="w-6 h-6" /></div>
                  <h3 className="font-bold mb-2 group-hover:underline">Quick Start Guide</h3>
                  <p className="text-sm text-zinc-500">Deploy IntellectSafe in 5 minutes using Docker.</p>
               </div>
               <div className="border border-zinc-200 p-6 rounded-lg hover:border-black transition-colors cursor-pointer group">
                  <div className="mb-4 text-blue-600"><Book className="w-6 h-6" /></div>
                  <h3 className="font-bold mb-2 group-hover:underline">API Reference</h3>
                  <p className="text-sm text-zinc-500">Explore our REST API details and examples.</p>
               </div>
            </div>

            <div className="bg-zinc-50 p-6 rounded-lg border border-zinc-200">
               <h3 className="font-bold mb-4 flex items-center gap-2">
                  <Terminal className="w-4 h-4" /> Installation
               </h3>
               <code className="block bg-zinc-900 text-zinc-100 p-4 rounded text-sm font-mono overflow-x-auto">
                  npm install @intellectsafe/sdk<br/>
                  # or<br/>
                  docker pull intellectsafe/core:latest
               </code>
            </div>
         </main>
      </div>
    </div>
  );
};

export default Docs;
