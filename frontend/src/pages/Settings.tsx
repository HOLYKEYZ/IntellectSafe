import { useState, useEffect } from 'react';
import { Key, User, Copy, Check, RefreshCw, AlertCircle } from 'lucide-react';
import { getCurrentUser, generateApiKey } from '@/lib/api';

const Settings = () => {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [showKey, setShowKey] = useState(false);
  const [copied, setCopied] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    getCurrentUser()
      .then((data) => setUser(data))
      .catch(() => {});
  }, []);

  const handleGenerateKey = async () => {
    setGenerating(true);
    setError('');
    try {
      const result = await generateApiKey();
      setApiKey(result.api_key);
      setShowKey(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate API key');
    } finally {
      setGenerating(false);
    }
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

      {error && (
        <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-md text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

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
            {apiKey && showKey ? (
              <div className="bg-muted p-4 rounded-md border border-dashed border-gray-300">
                <label className="text-xs font-bold uppercase text-gray-500 mb-2 block">Your New API Key</label>
                <div className="flex items-center space-x-2">
                  <code className="flex-1 font-mono text-sm bg-background p-3 rounded border break-all">
                    {apiKey}
                  </code>
                  <button
                    onClick={copyKey}
                    className="p-3 bg-background border rounded hover:bg-accent transition-colors"
                    title="Copy to clipboard"
                  >
                    {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
                <p className="text-xs text-amber-600 dark:text-amber-400 mt-2 font-medium">
                  ⚠️ Copy this key now — it will not be shown again.
                </p>
              </div>
            ) : (
              <div className="bg-muted p-4 rounded-md border border-dashed border-gray-300">
                <label className="text-xs font-bold uppercase text-gray-500 mb-2 block">API Key</label>
                <p className="text-sm text-muted-foreground">
                  {apiKey === null ? 'Generate a new API key to access the platform programmatically.' : 'Key hidden. Generate a new one if needed.'}
                </p>
              </div>
            )}

            <div className="flex justify-end">
              <button
                onClick={handleGenerateKey}
                disabled={generating}
                className="flex items-center space-x-2 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 px-4 py-2 rounded-md hover:bg-zinc-700 dark:hover:bg-zinc-200 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
                <span>{generating ? 'Generating...' : apiKey ? 'Rotate API Key' : 'Generate API Key'}</span>
              </button>
            </div>

            <div className="text-xs text-muted-foreground bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded text-yellow-800 dark:text-yellow-300 border border-yellow-100 dark:border-yellow-800">
              <strong>Security Note:</strong> Your key is hashed server-side. We never store the raw key. Previous keys are automatically deactivated when you generate a new one.
            </div>
          </div>
        </div>

      {/* Safety Scanner Section */}
      <div className="bg-card border rounded-lg p-6 shadow-sm">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <ShieldCheck className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">AI Safety Scanner</h2>
              <p className="text-sm text-muted-foreground">Select which AI model performs safety checks (Output Scanning & Prompt Injection).</p>
            </div>
          </div>
        </div>

        <SafetyModelSelector user={user} onUpdate={(updated) => setUser(updated)} />
      </div>

      {/* Connections Section (BYOK) */}
      <div className="bg-card border rounded-lg p-6 shadow-sm">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <RefreshCw className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Upstream Connections</h2>
              <p className="text-sm text-muted-foreground">Connect your AI provider accounts (BYOK).</p>
            </div>
          </div>
        </div>

        <ConnectionsManager />
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

// Sub-component for managing connections
import { getConnections, createConnection, deleteConnection, updateUser, Connection } from '@/lib/api';
import { Trash2, Plus, ShieldCheck } from 'lucide-react';

const SafetyModelSelector = ({ user, onUpdate }: { user: any, onUpdate: (u: any) => void }) => {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getConnections().then(setConnections).catch(console.error);
  }, []);

  const handleUpdate = async (provider: string) => {
    setLoading(true);
    try {
        const val = provider || null;
        const updated = await updateUser({ safety_provider: val });
        onUpdate(updated);
    } catch (err) {
        console.error("Failed to update safety provider", err);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
        <label className="block text-sm font-medium">Select Scanner Model</label>
        <select 
            value={user?.safety_provider || ""} 
            onChange={(e) => handleUpdate(e.target.value)}
            disabled={loading}
            className="w-full p-2 rounded border bg-background max-w-md"
        >
            <option value="">System Default (Optimized)</option>
            {connections.map(c => (
                <option key={c.id} value={c.provider}>
                    Use my {c.provider} key ({c.label || c.key_mask})
                </option>
            ))}
        </select>
        <p className="text-xs text-muted-foreground">
            Use one of your connected accounts to perform safety scans. 
            Useful if you want to use a specific model (e.g. Haiku, Flash) for speed/cost.
        </p>
    </div>
  );
};

const ConnectionsManager = () => {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [newKey, setNewKey] = useState('');
  const [provider, setProvider] = useState('openai');

  const fetchConnections = async () => {
    try {
      const data = await getConnections();
      setConnections(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnections();
  }, []);

  const handleAdd = async () => {
    if (!newKey) return;
    setLoading(true);
    try {
      await createConnection({ provider, api_key: newKey });
      setNewKey('');
      setAdding(false);
      await fetchConnections();
    } catch (err) {
      alert("Failed to add connection");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Remove this connection?")) return;
    try {
      await deleteConnection(id);
      setConnections(connections.filter(c => c.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        {connections.map((conn) => (
          <div key={conn.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-md border">
            <div className="flex items-center gap-3">
               <div className="bg-green-100 dark:bg-green-900/20 p-2 rounded-full">
                 <ShieldCheck className="w-4 h-4 text-green-700 dark:text-green-400" />
               </div>
               <div>
                 <p className="font-medium capitalize">{conn.provider} <span className="text-xs text-muted-foreground ml-2">({conn.key_mask})</span></p>
                 <p className="text-xs text-muted-foreground">Added on {new Date(conn.created_at).toLocaleDateString()}</p>
               </div>
            </div>
            <button
               onClick={() => handleDelete(conn.id)}
               className="text-red-500 hover:text-red-700 p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
        
        {connections.length === 0 && !loading && (
          <p className="text-sm text-muted-foreground text-center py-4 italic">No active connections. Add one below.</p>
        )}
      </div>

      {adding ? (
        <div className="border p-4 rounded-md space-y-4 bg-muted/30">
          <h3 className="font-medium text-sm">Add New Connection</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-medium mb-1">Provider</label>
              <select 
                value={provider} 
                onChange={(e) => setProvider(e.target.value)}
                className="w-full p-2 rounded border bg-background"
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic (Claude)</option>
                <option value="google">Google Gemini</option>
                <option value="groq">Groq</option>
                <option value="perplexity">Perplexity</option>
                <option value="openrouter">OpenRouter (Universal)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">API Key</label>
              <input 
                type="password" 
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                placeholder="sk-..." 
                className="w-full p-2 rounded border bg-background"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button onClick={() => setAdding(false)} className="px-3 py-1 text-sm border rounded hover:bg-accent">Cancel</button>
            <button onClick={handleAdd} className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:opacity-90">Securely Save</button>
          </div>
        </div>
      ) : (
        <button 
          onClick={() => setAdding(true)}
          className="flex items-center gap-2 text-sm text-primary hover:underline"
        >
          <Plus className="w-4 h-4" /> Connect New Account
        </button>
      )}
    </div>
  );
};

export default Settings;
