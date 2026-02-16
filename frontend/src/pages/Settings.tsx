
import { useState, useEffect } from 'react';
import { Key, User, Copy, Check, RefreshCw } from 'lucide-react';
import { getCurrentUser } from '@/lib/api';

const Settings = () => {
  const [apiKey, setApiKey] = useState<string | null>(localStorage.getItem('user_api_key'));
  const [copied, setCopied] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    getCurrentUser()
      .then((data) => setUser(data))
      .catch(() => {});
  }, []);

  const generateKey = () => {
    setGenerating(true);
    // Generate a cryptographically stronger key
    const array = new Uint8Array(24);
    crypto.getRandomValues(array);
    const newKey = 'is-' + Array.from(array, (b) => b.toString(16).padStart(2, '0')).join('');
    setApiKey(newKey);
    localStorage.setItem('user_api_key', newKey);
    setGenerating(false);
  };

  const copyKey = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-2">Manage your access and security preferences.</p>
      </div>

      <div className="grid gap-6">
        {/* API Key Section */}
        <div className="bg-card border rounded-lg p-6 shadow-sm">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Key className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">API Access</h2>
                <p className="text-sm text-muted-foreground">Manage your secret keys for programmatic access.</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-muted p-4 rounded-md border border-dashed border-gray-300">
              <label className="text-xs font-bold uppercase text-gray-500 mb-2 block">Your Active Key</label>
              <div className="flex items-center space-x-2">
                <code className="flex-1 font-mono text-sm bg-background p-3 rounded border">
                  {apiKey || "No API key generated"}
                </code>
                {apiKey && (
                  <button 
                    onClick={copyKey}
                    className="p-3 bg-background border rounded hover:bg-accent transition-colors"
                    title="Copy to clipboard"
                  >
                    {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                  </button>
                )}
              </div>
            </div>

            <div className="flex justify-end">
              <button 
                onClick={generateKey} 
                disabled={generating}
                className="flex items-center space-x-2 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 px-4 py-2 rounded-md hover:bg-zinc-700 dark:hover:bg-zinc-200 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
                <span>{apiKey ? 'Rotate API Key' : 'Generate API Key'}</span>
              </button>
            </div>
            
            <div className="text-xs text-muted-foreground bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded text-yellow-800 dark:text-yellow-300 border border-yellow-100 dark:border-yellow-800">
               <strong>Security Note:</strong> This key helps track your requests. Treat it like a password. Do not share it in client-side code.
            </div>
          </div>
        </div>

        {/* Profile Section */}
        <div className="bg-card border rounded-lg p-6 shadow-sm">
          <div className="flex items-center space-x-3 mb-6">
             <div className="p-2 bg-primary/10 rounded-lg">
                <User className="w-6 h-6 text-primary" />
             </div>
             <div>
                <h2 className="text-lg font-semibold">Profile Information</h2>
                <p className="text-sm text-muted-foreground">Your account details.</p>
             </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
             <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <input disabled value={user?.email || 'Loading...'} className="w-full p-2 bg-muted rounded border text-foreground" />
             </div>
             <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input disabled value={user?.full_name || 'N/A'} className="w-full p-2 bg-muted rounded border text-foreground" />
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
