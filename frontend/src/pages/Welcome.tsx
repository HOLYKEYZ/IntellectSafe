import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Activity, ChevronRight, Terminal, AlertTriangle, Eye, Zap, Fingerprint, Book, Code, Database } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const Welcome = () => {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [activeDocTab, setActiveDocTab] = useState('intro');
  
  const researchRef = useRef<HTMLDivElement>(null);
  const docsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (ref: React.RefObject<HTMLDivElement>) => {
    ref.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const renderDocContent = () => {
    switch (activeDocTab) {
      case 'intro':
        return (
          <div className="animate-in fade-in slide-in-from-right-4 duration-300">
            <h3 className="text-2xl font-bold mb-4 text-zinc-900 dark:text-zinc-100">The IntellectSafe Platform</h3>
            <p className="text-zinc-600 dark:text-zinc-400 mb-6 leading-relaxed">
              We are the only platform offering <b>Full-Spectrum AI Governance</b>. While others focus on basic string matching, IntellectSafe intercepts threats across the entire cognitive stack—from the initial user prompt to the final autonomous action.
            </p>
            <div className="bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 p-6 rounded-lg">
              <h4 className="font-bold mb-3 flex items-center gap-2 text-zinc-900 dark:text-zinc-100"><Activity className="w-4 h-4 text-emerald-600 dark:text-emerald-400"/> 5-Level Defense Engine</h4>
              <ul className="space-y-2 text-sm text-zinc-600 dark:text-zinc-400">
                <li className="flex gap-2"><span>•</span> <span><b>Level 1 (Input)</b>: Deep semantic analysis of user intent.</span></li>
                <li className="flex gap-2"><span>•</span> <span><b>Level 3 (Model)</b>: Real-time weight integrity & optimization checks.</span></li>
                <li className="flex gap-2"><span>•</span> <span><b>Level 5 (System)</b>: Autonomous agent behavior confinement.</span></li>
              </ul>
            </div>
          </div>
        );
      case 'quickstart':
        return (
          <div className="animate-in fade-in slide-in-from-right-4 duration-300">
             <h3 className="text-2xl font-bold mb-4 text-zinc-900 dark:text-zinc-100">Quick Start</h3>
             <p className="text-zinc-600 dark:text-zinc-400 mb-6">Deploy the defense layer in minutes using our Docker container.</p>
             
             <div className="mb-6">
               <div className="text-xs font-bold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-2">1. Pull Image</div>
               <code className="block bg-zinc-900 text-zinc-100 p-4 rounded text-sm font-mono overflow-x-auto">
                 docker pull intellectsafe/core:latest
               </code>
             </div>

             <div className="mb-6">
                <div className="text-xs font-bold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-2">2. Run Container</div>
                <code className="block bg-zinc-900 text-zinc-100 p-4 rounded text-sm font-mono overflow-x-auto">
                  docker run -p 8000:8000 \<br/>
                  &nbsp;&nbsp;-e OPENAI_API_KEY=sk-... \<br/>
                  &nbsp;&nbsp;intellectsafe/core
                </code>
             </div>
          </div>
        );
      case 'api':
        return (
           <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              <div className="flex justify-between items-center mb-4">
                 <h3 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">API Reference</h3>
                 <span className="px-2 py-1 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded uppercase">v1.0 Stable</span>
              </div>
              <p className="text-zinc-600 dark:text-zinc-400 mb-8">Direct REST API access for custom integrations.</p>

              <div className="space-y-8">
                 <div>
                    <div className="flex items-center gap-3 mb-3">
                       <span className="bg-blue-600 text-white px-2 py-1 text-xs font-bold rounded">POST</span>
                       <code className="text-sm font-mono bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 px-2 py-1 rounded">/v1/scan/prompt</code>
                    </div>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-3">Scans a raw input prompt for injection attacks and PII.</p>
                    <div className="bg-zinc-900 p-4 rounded text-xs font-mono text-zinc-300">
                       <span className="text-purple-400">curl</span> -X POST https://api.intellectsafe.com/v1/scan \<br/>
                       &nbsp;&nbsp;-d <span className="text-green-400">'{"{"} "prompt": "Ignore previous instructions..." {"}"}'</span>
                    </div>
                 </div>
              </div>
           </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 font-sans selection:bg-zinc-900 selection:text-white dark:selection:bg-white dark:selection:text-zinc-900 overflow-x-hidden relative transition-colors">
      
      {/* Background Grid Pattern - Increased Opacity */}
      <div className="fixed inset-0 z-0 opacity-[0.08] pointer-events-none" 
           style={{ backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', backgroundSize: '50px 50px' }}>
      </div>

      {/* Navigation */}
      <nav className={`fixed top-0 w-full px-6 py-4 flex justify-between items-center z-50 transition-all duration-500 ${scrolled ? 'bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md border-b border-zinc-100 dark:border-zinc-800' : 'bg-transparent'}`}>
        <div className="flex items-center gap-2 group cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
           <div className="w-12 h-12 flex items-center justify-center">
                           <img src="/logo.png" alt="IntellectSafe Logo" className="w-full h-full object-contain dark:invert" />
           </div>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium tracking-wide">
          <button onClick={() => navigate('/dashboard')} className="hover:text-zinc-500 transition-colors">Dashboard</button>
          <button onClick={() => navigate('/docs')} className="hover:text-zinc-500 transition-colors">Documentation</button>
          <a href={`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/docs`} target="_blank" rel="noopener noreferrer" className="hover:text-zinc-500 transition-colors">API Docs</a>
          <button onClick={() => scrollToSection(researchRef)} className="hover:text-zinc-500 transition-colors">Research</button>
        </div>

        
        <div className="flex items-center gap-4">
           <ThemeToggle />
           <button 
             onClick={() => navigate('/signup')} 
             className="hidden md:block text-sm font-medium hover:text-zinc-600 dark:hover:text-zinc-400 transition-colors"
           >
             Sign Up
           </button>
           <button 
             onClick={() => navigate('/login')}
             className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 px-5 py-2 text-sm font-medium hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-colors rounded-sm"
           >
             Login
           </button>

        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex flex-col md:flex-row h-screen pt-20 relative z-10 border-b border-zinc-100">
        {/* Left: Content */}
        <div className="w-full md:w-1/2 h-full flex flex-col justify-center px-8 md:px-24">
          <div className="max-w-2xl animate-in slide-in-from-bottom-10 fade-in duration-1000">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-zinc-100 dark:bg-zinc-800 rounded-full mb-8 border border-zinc-200 dark:border-zinc-700">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 dark:text-zinc-400">System V1.0 Online • Full Lifecycle Protection</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-serif font-medium leading-[0.95] mb-8 tracking-tight">
              Securing <br/>
              <span className="italic relative">
                intelligence
                <svg className="absolute -bottom-2 left-0 w-full h-3 text-emerald-500/20" viewBox="0 0 100 10" preserveAspectRatio="none">
                  <path d="M0 5 Q 50 10 100 5" stroke="currentColor" strokeWidth="2" fill="none" />
                </svg>
              </span> layers.
            </h1>
            
            <p className="text-lg text-zinc-600 dark:text-zinc-400 leading-relaxed max-w-lg mb-10 animate-in slide-in-from-bottom-5 fade-in duration-1000 delay-200">
               <span className="font-bold text-zinc-900 dark:text-zinc-100">IntellectSafe is the only platform</span> that secures the entire AI lifecycle. 
               We move beyond simple prompt filters to govern Human inputs, Model weights, and System actions in a single unified architecture.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 animate-in slide-in-from-bottom-5 fade-in duration-1000 delay-300">
              <button 
                onClick={() => navigate('/signup')}
                className="group bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 px-8 py-4 text-sm font-bold tracking-wider hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:-translate-y-1"
              >
                SECURE YOUR AI
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <button 
                 onClick={() => scrollToSection(researchRef)}
                className="group px-8 py-4 text-sm font-bold tracking-wider border border-zinc-200 dark:border-zinc-700 hover:border-zinc-900 dark:hover:border-zinc-400 transition-all hover:bg-zinc-50 dark:hover:bg-zinc-800 flex items-center justify-center gap-2"
              >
                LEARN MORE
              </button>
            </div>
          </div>
        </div>

        {/* Right: Visual */}
        <div className="w-full md:w-1/2 h-full relative bg-zinc-50 dark:bg-zinc-950 flex items-center justify-center overflow-hidden border-l border-zinc-100 dark:border-zinc-800">
             <div className="absolute inset-0 z-10 pointer-events-none bg-gradient-to-b from-transparent via-emerald-500/5 to-transparent h-[20%] w-full animate-[scan_4s_ease-in-out_infinite]"></div>
             {/* Light mode image */}
             <img 
               src="/hero-image.png" 
               alt="Robotic arm reaching for human hand" 
               className="w-full h-full object-cover grayscale contrast-125 mix-blend-multiply scale-105 animate-[pulse_10s_ease-in-out_infinite] dark:hidden"
             />
             {/* Dark mode image */}
             <img 
               src="/hero-image-dark.png" 
               alt="Robotic arm reaching for human hand" 
               className="w-full h-full object-cover scale-105 animate-[pulse_10s_ease-in-out_infinite] hidden dark:block"
             />
             <div className="absolute bottom-10 right-10 bg-white/90 dark:bg-zinc-900/90 backdrop-blur border border-zinc-200 dark:border-zinc-700 p-4 rounded-sm shadow-sm z-20 animate-in slide-in-from-right-10 fade-in duration-1000 delay-700">
                <div className="flex items-center gap-3 mb-2">
                   <Activity className="w-4 h-4 text-emerald-500" />
                   <span className="text-xs font-bold uppercase tracking-widest mb-0 text-zinc-900 dark:text-zinc-100">System Activity</span>
                </div>
                <div className="space-y-1">
                   <div className="h-1 w-32 bg-zinc-100 dark:bg-zinc-700 rounded-full overflow-hidden">
                      <div className="h-full bg-zinc-900 dark:bg-emerald-500 w-[70%] animate-[width_2s_ease-in-out_infinite]"></div>
                   </div>
                   <div className="flex justify-between text-[10px] text-zinc-400 font-mono">
                      <span>REQ/S</span>
                      <span>2,401</span>
                   </div>
                </div>
             </div>
        </div>
      </main>

      {/* PROBLEM OVERVIEW (Hidden Dangers) */}
      <section className="py-24 bg-white dark:bg-zinc-900 relative z-10 border-b border-zinc-100 dark:border-zinc-800">
        <div className="container mx-auto px-6">
           <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl md:text-5xl font-serif mb-6 text-zinc-900 dark:text-zinc-100">The Hidden Dangers of Large Language Models</h2>
              <p className="text-zinc-600 dark:text-zinc-400 text-lg leading-relaxed">
                 As AI integrates into critical infrastructure, the attack surface expands. 
                 Models are vulnerable to unique adversarial attacks that traditional security tools cannot detect.
              </p>
           </div>
           
           {/* High-level cards */}
           <div className="grid md:grid-cols-3 gap-8">
              <div className="p-8 border border-zinc-100 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                 <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-500 mb-4" />
                 <h3 className="text-xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">Jailbreaks</h3>
                 <p className="text-zinc-600 dark:text-zinc-400 text-sm">Bypassing safety filters to generate harmful, illegal, or unethical content.</p>
              </div>
              <div className="p-8 border border-zinc-100 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                 <Eye className="w-8 h-8 text-blue-600 dark:text-blue-500 mb-4" />
                 <h3 className="text-xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">Privacy Leaks</h3>
                 <p className="text-zinc-600 dark:text-zinc-400 text-sm">Extraction of PII or proprietary training data via specific prompting.</p>
              </div>
              <div className="p-8 border border-zinc-100 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                 <Fingerprint className="w-8 h-8 text-purple-600 dark:text-purple-500 mb-4" />
                 <h3 className="text-xl font-bold mb-2 text-zinc-900 dark:text-zinc-100">Deepfakes</h3>
                 <p className="text-zinc-600 dark:text-zinc-400 text-sm">Generation of indistinguishable synthetic media for fraud or disinformation.</p>
              </div>
           </div>
        </div>
      </section>

      {/* DEEP RESEARCH SECTION - THE 5-LEVEL THREAT MATRIX */}
      <section ref={researchRef} className="py-24 bg-zinc-50 dark:bg-zinc-800 relative z-10 border-b border-zinc-200 dark:border-zinc-700">
         <div className="container mx-auto px-6">
            <div className="flex items-center gap-4 mb-12">
               <div className="h-px bg-zinc-300 dark:bg-zinc-600 flex-1"></div>
               <span className="text-xs font-bold uppercase tracking-widest text-zinc-400 dark:text-zinc-500">Comprehensive Threat Matrix</span>
               <div className="h-px bg-zinc-300 dark:bg-zinc-600 flex-1"></div>
            </div>

            <header className="mb-16 max-w-4xl mx-auto text-center">
               <h2 className="text-4xl md:text-5xl font-serif font-medium mb-6 text-zinc-900 dark:text-zinc-100">Full-Spectrum AI Defense</h2>
               <p className="text-xl text-zinc-600 dark:text-zinc-400 leading-relaxed">
                 We don't just stop at prompt injection. IntellectSafe secures the entire AI lifecycle across 5 critical threat levels.
               </p>
            </header>

            <div className="grid gap-12 max-w-6xl mx-auto">
               
               {/* LEVEL 1: INPUT SIDE THREATS */}
               <div className="bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
                  <div className="bg-zinc-900 px-8 py-4 flex items-center justify-between">
                     <div className="flex items-center gap-3">
                        <Terminal className="w-5 h-5 text-emerald-400" />
                        <h3 className="text-white font-bold tracking-wide">LEVEL 1: INPUT SIDE THREATS</h3>
                     </div>
                     <span className="text-xs font-mono text-zinc-400">ATTACK_VECTOR::PROMPT</span>
                  </div>
                  <div className="p-8 grid md:grid-cols-2 gap-8">
                     <div>
                        <h4 className="font-bold text-lg mb-4 text-zinc-900 dark:text-zinc-100 border-b border-zinc-100 dark:border-zinc-700 pb-2">Direct Injection</h4>
                        <ul className="space-y-3">
                           <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                              <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5"/>
                              <div><strong className="text-zinc-900 dark:text-zinc-100">Prompt Injection & Manipulation</strong>: Overriding system instructions using sophisticated command syntax.</div>
                           </li>
                           <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                              <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5"/>
                              <div><strong className="text-zinc-900 dark:text-zinc-100">Role Hijacking</strong>: Forcing the AI into a persona (e.g., "Mongo Tom") that ignores safety protocols.</div>
                           </li>
                           <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                              <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5"/>
                              <div><strong className="text-zinc-900 dark:text-zinc-100">Context Poisoning</strong>: Injecting malicious data into RAG context windows to warp model reality.</div>
                           </li>
                        </ul>
                     </div>
                     <div>
                        <h4 className="font-bold text-lg mb-4 text-zinc-900 dark:text-zinc-100 border-b border-zinc-100 dark:border-zinc-700 pb-2">Obfuscation</h4>
                        <ul className="space-y-3">
                           <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                              <Lock className="w-4 h-4 text-orange-500 shrink-0 mt-0.5"/>
                              <div><strong className="text-zinc-900 dark:text-zinc-100">Instruction Smuggling</strong>: Hiding commands inside seemingly benign tasks or code blocks.</div>
                           </li>
                           <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                              <Code className="w-4 h-4 text-orange-500 shrink-0 mt-0.5"/>
                              <div><strong className="text-zinc-900 dark:text-zinc-100">Encoded Attacks</strong>: Bypassing filters using Base64, JSON, or Morse code payloads that the model decodes internally.</div>
                           </li>
                        </ul>
                     </div>
                  </div>
               </div>

               {/* LEVEL 2: OUTPUT SIDE THREATS */}
               <div className="bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
                  <div className="bg-zinc-900 px-8 py-4 flex items-center justify-between">
                     <div className="flex items-center gap-3">
                        <Activity className="w-5 h-5 text-blue-400" />
                        <h3 className="text-white font-bold tracking-wide">LEVEL 2: OUTPUT SIDE THREATS</h3>
                     </div>
                     <span className="text-xs font-mono text-zinc-400">ATTACK_VECTOR::RESPONSE</span>
                  </div>
                  <div className="p-8 grid md:grid-cols-2 gap-8">
                     <ul className="space-y-3">
                         <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                           <Shield className="w-4 h-4 text-blue-500 shrink-0 mt-0.5"/>
                           <div><strong className="text-zinc-900 dark:text-zinc-100">Policy Evasion</strong>: Generating harmful content that skirts the edge of safety guidelines.</div>
                        </li>
                        <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                           <Eye className="w-4 h-4 text-blue-500 shrink-0 mt-0.5"/>
                           <div><strong className="text-zinc-900 dark:text-zinc-100">Data Leakage</strong>: Inadvertent revelation of PII, credentials, or proprietary training data.</div>
                        </li>
                        <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                           <Book className="w-4 h-4 text-blue-500 shrink-0 mt-0.5"/>
                           <div><strong className="text-zinc-900 dark:text-zinc-100">Hallucinated Authority</strong>: Confidently false information presented as expert fact (Disinformation).</div>
                        </li>
                     </ul>
                      <ul className="space-y-3">
                         <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                           <Zap className="w-4 h-4 text-blue-500 shrink-0 mt-0.5"/>
                           <div><strong className="text-zinc-900 dark:text-zinc-100">Harmful Completion</strong>: Successfully generating malware code, hate speech, or dangerous chemistry instructions.</div>
                        </li>
                        <li className="flex gap-3 text-sm text-zinc-600 dark:text-zinc-400">
                           <Activity className="w-4 h-4 text-blue-500 shrink-0 mt-0.5"/>
                           <div><strong className="text-zinc-900 dark:text-zinc-100">Unsafe Reasoning Chains</strong>: Internal monologues that justify unethical decisions.</div>
                        </li>
                     </ul>
                  </div>
               </div>

               {/* LEVEL 3 & 4: MODEL & HUMAN THREATS */}
               <div className="grid md:grid-cols-2 gap-8">
                   {/* Level 3 */}
                   <div className="bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
                       <div className="bg-zinc-900 px-6 py-3 border-b border-zinc-800">
                          <h3 className="text-white font-bold text-sm tracking-wide flex items-center gap-2">
                             <Database className="w-4 h-4 text-purple-400"/> LEVEL 3: MODEL LAYER
                          </h3>
                       </div>
                       <div className="p-6">
                          <ul className="space-y-4">
                             <li className="text-sm text-zinc-600 dark:text-zinc-400">
                                <strong className="block text-zinc-900 dark:text-zinc-100 mb-1">Model Extraction</strong>
                                Stealing the model's weights or capabilities via massive API querying.
                             </li>
                             <li className="text-sm text-zinc-600 dark:text-zinc-400">
                                <strong className="block text-zinc-900 dark:text-zinc-100 mb-1">Training Data Poisoning</strong>
                                Injecting "sleeper agents" or backdoors into the training set.
                             </li>
                             <li className="text-sm text-zinc-600 dark:text-zinc-400">
                                <strong className="block text-zinc-900 dark:text-zinc-100 mb-1">Over-Optimization Loops</strong>
                                Exploiting reward functions to create "wireheading" behavior.
                             </li>
                          </ul>
                       </div>
                   </div>

                   {/* Level 4 */}
                   <div className="bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden">
                       <div className="bg-zinc-900 px-6 py-3 border-b border-zinc-800">
                          <h3 className="text-white font-bold text-sm tracking-wide flex items-center gap-2">
                             <Fingerprint className="w-4 h-4 text-pink-400"/> LEVEL 4: HUMAN LAYER
                          </h3>
                       </div>
                       <div className="p-6">
                           <ul className="space-y-4">
                             <li className="text-sm text-zinc-600 dark:text-zinc-400">
                                <strong className="block text-zinc-900 dark:text-zinc-100 mb-1">Deepfakes & Synthetic Media</strong>
                                AI-generated video/audio for identity fraud and impersonation.
                             </li>
                             <li className="text-sm text-zinc-600 dark:text-zinc-400">
                                <strong className="block text-zinc-900 dark:text-zinc-100 mb-1">AI Impersonation</strong>
                                Bots mimicking humans to conduct social engineering attacks.
                             </li>
                             <li className="text-sm text-zinc-600 dark:text-zinc-400">
                                <strong className="block text-zinc-900 dark:text-zinc-100 mb-1">Automated Misinformation</strong>
                                Infinite scale generation of fake news and propaganda.
                             </li>
                          </ul>
                       </div>
                   </div>
               </div>

               {/* LEVEL 5: SYSTEM AGENTS */}
               <div className="bg-zinc-900 text-zinc-300 rounded-lg p-8 relative overflow-hidden border border-zinc-800">
                  <div className="relative z-10 flex flex-col md:flex-row gap-8 items-start">
                     <div className="md:w-1/3">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-red-500/10 rounded-full mb-4 border border-red-500/20">
                           <AlertTriangle className="w-4 h-4 text-red-500" />
                           <span className="text-[10px] font-bold uppercase tracking-widest text-red-400">Emerging Threat</span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-2">LEVEL 5: SYSTEM AGENTS</h3>
                        <p className="text-sm leading-relaxed text-zinc-400">
                           As AIs gain tool use and autonomy, the risks escalate from "bad words" to "bad actions".
                        </p>
                     </div>
                     <div className="md:w-2/3 grid grid-cols-2 gap-6">
                        <div>
                           <div className="text-white font-bold mb-1">Runaway Agents</div>
                           <p className="text-xs text-zinc-500">Autonomous loops where agents consume infinite resources or diverge from goals.</p>
                        </div>
                         <div>
                           <div className="text-white font-bold mb-1">Tool Abuse</div>
                           <p className="text-xs text-zinc-500">Using authorized API connections (Email, SQL, Stripe) for destructive ends.</p>
                        </div>
                         <div>
                           <div className="text-white font-bold mb-1">Permission Bypass</div>
                           <p className="text-xs text-zinc-500">Escalating privileges within the deployment environment.</p>
                        </div>
                         <div>
                           <div className="text-white font-bold mb-1">Autonomous Escalation</div>
                           <p className="text-xs text-zinc-500">Self-improving attacks that adapt to defenses in real-time.</p>
                        </div>
                     </div>
                  </div>
               </div>

            </div>
         </div>
      </section>

      {/* DOCS HUB SECTION */}
      <section ref={docsRef} className="py-24 bg-white dark:bg-zinc-900 relative z-10">
         <div className="container mx-auto px-6">
             <div className="flex items-center gap-4 mb-12">
               <div className="h-px bg-zinc-300 dark:bg-zinc-600 flex-1"></div>
               <span className="text-xs font-bold uppercase tracking-widest text-zinc-400 dark:text-zinc-500">Developer Hub</span>
               <div className="h-px bg-zinc-300 dark:bg-zinc-600 flex-1"></div>
            </div>

            <h2 className="text-4xl md:text-5xl font-serif font-medium mb-12 text-center text-zinc-900 dark:text-zinc-100">Documentation</h2>
            
            <div className="flex flex-col md:flex-row max-w-6xl mx-auto border border-zinc-200 dark:border-zinc-700 rounded-xl overflow-hidden shadow-2xl">
               {/* Sidebar Navigator */}
               <div className="md:w-64 bg-zinc-50 dark:bg-zinc-800 border-r border-zinc-200 dark:border-zinc-700 p-6 flex flex-col gap-2">
                  <div className="text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-4">Resources</div>
                  <button 
                     onClick={() => setActiveDocTab('intro')}
                     className={`text-left px-4 py-3 rounded-md text-sm font-medium transition-colors ${activeDocTab === 'intro' ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200 dark:border-zinc-600' : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-700'}`}
                  >
                     Introduction
                  </button>
                  <button 
                     onClick={() => setActiveDocTab('quickstart')}
                     className={`text-left px-4 py-3 rounded-md text-sm font-medium transition-colors ${activeDocTab === 'quickstart' ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200 dark:border-zinc-600' : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-700'}`}
                  >
                     Quick Start
                  </button>
                  <button 
                     onClick={() => setActiveDocTab('api')}
                     className={`text-left px-4 py-3 rounded-md text-sm font-medium transition-colors ${activeDocTab === 'api' ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 shadow-sm border border-zinc-200 dark:border-zinc-600' : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-700'}`}
                  >
                     API Reference
                  </button>
               </div>

               {/* Content Area */}
               <div className="flex-1 bg-white dark:bg-zinc-900 p-12 min-h-[500px]">
                  {renderDocContent()}
               </div>
            </div>
         </div>
      </section>

      {/* Footer */}
      <footer className="bg-zinc-900 text-white py-12 border-t border-zinc-800">
         <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center opacity-60 text-sm">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
               {/* Footer logo also cleaned up */}
               <img src="/logo.png" className="w-4 h-4 invert" alt="Logo"/>
               <span className="font-bold tracking-widest">INTELLECTSAFE</span>
            </div>
            <div>
               &copy; 2026 IntellectSafe Inc. All rights reserved.
            </div>
         </div>
      </footer>
    </div>
  );
};
export default Welcome;
