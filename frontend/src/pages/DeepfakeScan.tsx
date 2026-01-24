
import React, { useState } from 'react';
import { Upload, FileText, Image as ImageIcon, Video, Mic, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { scanContent, ScanResponse } from '../lib/api';

const DeepfakeScan = () => {
  const [activeTab, setActiveTab] = useState<'text' | 'image' | 'video' | 'audio'>('text');
  const [content, setContent] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
      // Convert to base64 for preview/sending
      const reader = new FileReader();
      reader.onload = (ev) => {
        setContent(ev.target?.result as string || '');
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  };

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      if (!content) throw new Error("Please provide content to scan.");
      
      const response = await scanContent({
        content_type: activeTab,
        content: content, // Base64 or text
      });
      setResult(response);
    } catch (err: any) {
      setError(err.message || "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'text', label: 'AI Text', icon: FileText },
    { id: 'image', label: 'Deepfake Image', icon: ImageIcon },
    { id: 'audio', label: 'Voice Clone', icon: Mic },
    { id: 'video', label: 'Synth Video', icon: Video },
  ] as const;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Deepfake Detector</h1>
        <p className="text-muted-foreground mt-2">Analyze multi-modal content for synthetic manipulation.</p>
      </div>

      <div className="flex space-x-1 bg-muted p-1 rounded-lg w-fit">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => { setActiveTab(tab.id as any); setResult(null); setContent(''); setFile(null); }}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id 
                ? 'bg-background text-foreground shadow-sm' 
                : 'text-muted-foreground hover:bg-background/50'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-card border rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4">Input Source</h2>
            
            {activeTab === 'text' ? (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste suspicious text here..."
                className="w-full h-64 p-4 rounded-md border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary"
              />
            ) : (
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-12 text-center hover:bg-accent/50 transition-colors relative">
                <input 
                  type="file" 
                  accept={activeTab === 'image' ? "image/*" : activeTab === 'audio' ? "audio/*" : "video/*"}
                  onChange={handleFileChange}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <div className="space-y-2">
                  <Upload className="w-10 h-10 mx-auto text-gray-400" />
                  <p className="text-sm font-medium">Click to upload {activeTab}</p>
                  <p className="text-xs text-muted-foreground">Supports standard formats</p>
                </div>
              </div>
            )}

            {file && activeTab !== 'text' && (
               <div className="mt-4 p-3 bg-muted rounded flex items-center justify-between">
                 <span className="text-sm font-medium truncate">{file.name}</span>
                 <span className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
               </div>
            )}
            
            <button
              onClick={handleScan}
              disabled={loading || !content}
              className="w-full mt-4 bg-primary text-primary-foreground py-3 rounded-md font-medium disabled:opacity-50 hover:bg-primary/90 transition-colors flex items-center justify-center space-x-2"
            >
              {loading ? (
                <span>Scanning...</span>
              ) : (
                <>
                  <ScanResponseIcon />
                  <span>Analyze Content</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Panel */}
        <div className="space-y-4">
          {result && (
            <div className="bg-card border rounded-lg p-6 shadow-sm animate-in fade-in slide-in-from-bottom-4">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-semibold">Analysis Result</h2>
                  <p className="text-sm text-muted-foreground">ID: {result.scan_request_id.slice(0, 8)}</p>
                </div>
                <div className={`px-4 py-1 rounded-full text-sm font-bold uppercase tracking-wider ${
                  result.verdict === 'blocked' ? 'bg-red-100 text-red-700' :
                  result.risk_level === 'high' ? 'bg-orange-100 text-orange-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {result.verdict}
                </div>
              </div>

              <div className="space-y-6">
                <div className="flex items-center space-x-4">
                  <div className={`w-20 h-20 rounded-full flex items-center justify-center border-4 ${
                    result.risk_score > 80 ? 'border-red-500 text-red-600' :
                    result.risk_score > 50 ? 'border-orange-500 text-orange-600' :
                    'border-green-500 text-green-600'
                  }`}>
                    <div className="text-center">
                      <span className="text-2xl font-bold">{Math.round(result.risk_score)}</span>
                      <span className="block text-[10px] uppercase font-bold text-gray-400">Score</span>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-medium text-lg">
                      {result.risk_score > 80 ? 'High Probability AI' :
                       result.risk_score > 50 ? 'Suspicious Content' : 'Likely Authentic'}
                    </h3>
                    <p className="text-sm text-muted-foreground">Confidence: {(result.confidence * 100).toFixed(1)}%</p>
                  </div>
                </div>

                <div className="bg-muted p-4 rounded-md">
                   <h4 className="text-sm font-bold uppercase mb-2 text-gray-500">Explanation</h4>
                   <p className="text-sm leading-relaxed">{result.explanation}</p>
                </div>

                {result.signals && Object.keys(result.signals).length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold uppercase mb-3 text-gray-500">Detection Signals</h4>
                    <div className="grid grid-cols-2 gap-2">
                       {Object.entries(result.signals).map(([key, value]) => (
                         <div key={key} className="bg-background border p-2 rounded text-xs flex justify-between">
                            <span className="font-mono text-gray-600">{key}</span>
                            <span className="font-bold text-right truncate max-w-[150px]" title={typeof value === 'object' ? JSON.stringify(value) : String(value)}>
                              {typeof value === 'object' ? JSON.stringify(value).slice(0, 20) + '...' : String(value)}
                            </span>
                         </div>
                       ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-md flex items-center space-x-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {!result && !error && (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 text-gray-400 border-2 border-dashed rounded-lg">
               <ImageIcon className="w-12 h-12 mb-4 opacity-20" />
               <p>Results will appear here after analysis.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ScanResponseIcon = () => (
  <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4" xmlns="http://www.w3.org/2000/svg"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
);

export default DeepfakeScan;
