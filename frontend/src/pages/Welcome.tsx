import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Activity, ChevronRight, Terminal, AlertTriangle, Eye, Server } from 'lucide-react';

const Welcome = () => {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-white text-zinc-900 font-sans selection:bg-zinc-900 selection:text-white overflow-x-hidden relative">
      
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 z-0 opacity-[0.03] pointer-events-none" 
           style={{ backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', backgroundSize: '50px 50px' }}>
      </div>

      {/* Navigation */}
      <nav className={`fixed top-0 w-full px-6 py-4 flex justify-between items-center z-50 transition-all duration-500 ${scrolled ? 'bg-white/80 backdrop-blur-md border-b border-zinc-100' : 'bg-transparent'}`}>
        <div className="flex items-center gap-2 group cursor-pointer" onClick={() => navigate('/dashboard')}>
           <div className="w-8 h-8 flex items-center justify-center">
             <img src="/logo.png" alt="IntellectSafe Logo" className="w-full h-full object-contain filter brightness-0" />
           </div>
           <span className="text-lg font-bold tracking-tight group-hover:opacity-70 transition-opacity">IntellectSafe</span>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium tracking-wide">
          <button onClick={() => navigate('/dashboard')} className="hover:text-zinc-500 transition-colors">Platform</button>
          <button onClick={() => navigate('/docs')} className="hover:text-zinc-500 transition-colors">Documentation</button>
          <button onClick={() => navigate('/research')} className="hover:text-zinc-500 transition-colors">Research</button>
        </div>
        
        <div className="flex items-center gap-4">
           <button 
             onClick={() => navigate('/signup')} 
             className="hidden md:block text-sm font-medium hover:text-zinc-600 transition-colors"
           >
             Sign Up
           </button>
           <button 
             onClick={() => navigate('/login')}
             className="bg-zinc-900 text-white px-5 py-2 text-sm font-medium hover:bg-zinc-800 transition-colors rounded-sm"
           >
             Login
           </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex flex-col md:flex-row h-screen pt-20 relative z-10">
        
        {/* Left: Content */}
        <div className="w-full md:w-1/2 h-full flex flex-col justify-center px-8 md:px-24">
          <div className="max-w-2xl animate-in slide-in-from-bottom-10 fade-in duration-1000">
            
             {/* Status Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-zinc-100 rounded-full mb-8 border border-zinc-200">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">Defense Architecture v1.0 ONLINE</span>
            </div>

            <h1 className="text-6xl md:text-8xl font-serif font-medium leading-[0.95] mb-8 tracking-tight">
              Securing <br/>
              <span className="italic relative">
                intelligence
                {/* Underline decoration */}
                <svg className="absolute -bottom-2 left-0 w-full h-3 text-emerald-500/20" viewBox="0 0 100 10" preserveAspectRatio="none">
                  <path d="M0 5 Q 50 10 100 5" stroke="currentColor" strokeWidth="2" fill="none" />
                </svg>
              </span> layer.
            </h1>
            
            <p className="text-lg text-zinc-600 leading-relaxed max-w-lg mb-10 animate-in slide-in-from-bottom-5 fade-in duration-1000 delay-200">
               Comprehensive protection against AI abuse and unchecked vulnerabilities.
               We provide the security infrastructure to prevent prompt injection, jailbreaks, and data leakage.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 animate-in slide-in-from-bottom-5 fade-in duration-1000 delay-300">
              <button 
                onClick={() => navigate('/signup')}
                className="group bg-zinc-900 text-white px-8 py-4 text-sm font-bold tracking-wider hover:bg-zinc-800 transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:-translate-y-1"
              >
                SECURE YOUR AI
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <button 
                 onClick={() => navigate('/research')}
                className="group px-8 py-4 text-sm font-bold tracking-wider border border-zinc-200 hover:border-zinc-900 transition-all hover:bg-zinc-50 flex items-center justify-center gap-2"
              >
                LEARN MORE
              </button>
            </div>
          </div>
        </div>

        {/* Right: Visual */}
        <div className="w-full md:w-1/2 h-full relative bg-zinc-50 flex items-center justify-center overflow-hidden border-l border-zinc-100">
            {/* Animated Scan Line Overlay */}
             <div className="absolute inset-0 z-10 pointer-events-none bg-gradient-to-b from-transparent via-emerald-500/5 to-transparent h-[20%] w-full animate-[scan_4s_ease-in-out_infinite]"></div>
             
             <img 
               src="/hero-image.png" 
               alt="Robotic arm reaching for human hand" 
               className="w-full h-full object-cover grayscale contrast-125 mix-blend-multiply scale-105 animate-[pulse_10s_ease-in-out_infinite]"
             />
             
             {/* Tech Overlay Details */}
             <div className="absolute bottom-10 right-10 bg-white/90 backdrop-blur border border-zinc-200 p-4 rounded-sm shadow-sm z-20 animate-in slide-in-from-right-10 fade-in duration-1000 delay-700">
                <div className="flex items-center gap-3 mb-2">
                   <Activity className="w-4 h-4 text-emerald-500" />
                   <span className="text-xs font-bold uppercase tracking-widest mb-0">System Activity</span>
                </div>
                <div className="space-y-1">
                   <div className="h-1 w-32 bg-zinc-100 rounded-full overflow-hidden">
                      <div className="h-full bg-zinc-900 w-[70%] animate-[width_2s_ease-in-out_infinite]"></div>
                   </div>
                   <div className="flex justify-between text-[10px] text-zinc-400 font-mono">
                      <span>REQ/S</span>
                      <span>2,401</span>
                   </div>
                </div>
             </div>
        </div>
      </main>

      {/* Details Section */}
      <section className="py-24 bg-zinc-50 relative z-10 border-t border-zinc-200">
        <div className="container mx-auto px-6">
           <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl md:text-5xl font-serif mb-6">The Hidden Dangers of Large Language Models</h2>
              <p className="text-zinc-600 text-lg leading-relaxed">
                 As AI integrates into critical infrastructure, the attack surface expands. 
                 Without specific defenses, models are vulnerable to manipulation, data exfiltration, 
                 and unintended behaviors that compromise organizational security.
              </p>
           </div>

           <div className="grid md:grid-cols-3 gap-8">
              {/* Card 1 */}
              <div className="bg-white p-8 border border-zinc-200 shadow-sm hover:shadow-md transition-shadow">
                 <div className="w-12 h-12 bg-red-50 flex items-center justify-center mb-6 rounded-sm">
                    <AlertTriangle className="w-6 h-6 text-red-600" />
                 </div>
                 <h3 className="text-xl font-bold mb-4">Prompt Injection</h3>
                 <p className="text-zinc-600 text-sm leading-relaxed">
                    Adversaries can override model instructions to force unauthorized actions, bypass safety filters, 
                    and execute malicious tasks using hidden commands.
                 </p>
              </div>

               {/* Card 2 */}
              <div className="bg-white p-8 border border-zinc-200 shadow-sm hover:shadow-md transition-shadow">
                 <div className="w-12 h-12 bg-blue-50 flex items-center justify-center mb-6 rounded-sm">
                    <Eye className="w-6 h-6 text-blue-600" />
                 </div>
                 <h3 className="text-xl font-bold mb-4">Data Leakage</h3>
                 <p className="text-zinc-600 text-sm leading-relaxed">
                    Unprotected models may inadvertently reveal PII, proprietary code, or confidential internal data 
                    when prompted with specific social engineering techniques.
                 </p>
              </div>

               {/* Card 3 */}
              <div className="bg-white p-8 border border-zinc-200 shadow-sm hover:shadow-md transition-shadow">
                 <div className="w-12 h-12 bg-zinc-900 flex items-center justify-center mb-6 rounded-sm">
                    <Shield className="w-6 h-6 text-white" />
                 </div>
                 <h3 className="text-xl font-bold mb-4">IntellectSafe Defense</h3>
                 <p className="text-zinc-600 text-sm leading-relaxed">
                    Our multi-layered validation engine acts as a firewall for cognition. 
                    Every prompt is scanned by a council of models and heuristic engines before it ever reaches your AI.
                 </p>
                 <div className="mt-6 pt-6 border-t border-zinc-100 flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-emerald-600">
                    <Server className="w-4 h-4" />
                    <span>Real-time Protection</span>
                 </div>
              </div>
           </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-zinc-900 text-white py-12 border-t border-zinc-800">
         <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center opacity-60 text-sm">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
               <img src="/logo.png" className="w-4 h-4 filter invert" alt="Logo"/>
               <span className="font-bold tracking-widest">INTELLECTSAFE</span>
            </div>
            <div>
               &copy; 2025 IntellectSafe Inc. All rights reserved.
            </div>
         </div>
      </footer>
    </div>
  );
};

export default Welcome;
