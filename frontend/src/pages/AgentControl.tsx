import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { authorizeAgent, killAgent, getAgentHistory, AgentAuthorizeRequest, AgentKillRequest } from '@/lib/api';
import { Shield, XCircle, CheckCircle, History, Zap } from 'lucide-react';

export default function AgentControl() {
  const [agentId, setAgentId] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [actionType, setActionType] = useState('file_read');
  const [actionPayload, setActionPayload] = useState('{"path": "/tmp/test.txt"}');
  const [authResult, setAuthResult] = useState<any>(null);
  const [killResult, setKillResult] = useState<any>(null);
  const [history, setHistory] = useState<any>(null);
  const [loading, setLoading] = useState('');
  const [error, setError] = useState('');

  const handleAuthorize = async () => {
    if (!agentId || !sessionId) return;
    setLoading('authorize');
    setError('');
    try {
      const request: AgentAuthorizeRequest = {
        agent_id: agentId,
        session_id: sessionId,
        action_type: actionType,
        requested_action: JSON.parse(actionPayload),
      };
      const result = await authorizeAgent(request);
      setAuthResult(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authorization failed');
    } finally {
      setLoading('');
    }
  };

  const handleKill = async () => {
    if (!agentId) return;
    setLoading('kill');
    setError('');
    try {
      const request: AgentKillRequest = {
        agent_id: agentId,
        session_id: sessionId || undefined,
        reason: 'Manual kill switch activated via dashboard',
      };
      const result = await killAgent(request);
      setKillResult(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kill switch failed');
    } finally {
      setLoading('');
    }
  };

  const handleHistory = async () => {
    if (!agentId) return;
    setLoading('history');
    setError('');
    try {
      const result = await getAgentHistory(agentId, sessionId || undefined);
      setHistory(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch history');
    } finally {
      setLoading('');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Agent Control</h1>
        <p className="text-muted-foreground">Level 5 — Authorize, monitor, and kill autonomous agents</p>
      </div>

      {error && (
        <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-md text-sm">
          {error}
        </div>
      )}

      {/* Agent Identity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Agent Identity
          </CardTitle>
          <CardDescription>Enter the agent and session identifiers</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold uppercase text-muted-foreground mb-2 block">Agent ID</label>
              <input
                value={agentId}
                onChange={(e) => setAgentId(e.target.value)}
                placeholder="agent-1"
                className="w-full p-3 border rounded-md bg-background text-foreground font-mono text-sm"
              />
            </div>
            <div>
              <label className="text-xs font-bold uppercase text-muted-foreground mb-2 block">Session ID</label>
              <input
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                placeholder="session-abc123"
                className="w-full p-3 border rounded-md bg-background text-foreground font-mono text-sm"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Authorization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Authorize Action
          </CardTitle>
          <CardDescription>Submit an agent action for security review</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-xs font-bold uppercase text-muted-foreground mb-2 block">Action Type</label>
            <select
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              className="w-full p-3 border rounded-md bg-background text-foreground text-sm"
            >
              <option value="file_read">file_read</option>
              <option value="file_write">file_write</option>
              <option value="file_delete">file_delete</option>
              <option value="network_request">network_request</option>
              <option value="code_execution">code_execution</option>
              <option value="database_query">database_query</option>
              <option value="system_command">system_command</option>
              <option value="api_call">api_call</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-bold uppercase text-muted-foreground mb-2 block">Action Payload (JSON)</label>
            <textarea
              value={actionPayload}
              onChange={(e) => setActionPayload(e.target.value)}
              className="w-full min-h-[100px] p-3 border rounded-md bg-background text-foreground font-mono text-sm"
              placeholder='{"path": "/tmp/test.txt"}'
            />
          </div>
          <Button onClick={handleAuthorize} disabled={loading === 'authorize' || !agentId || !sessionId}>
            {loading === 'authorize' ? 'Authorizing...' : 'Submit for Authorization'}
          </Button>

          {authResult && (
            <div className="mt-4 p-4 bg-muted rounded-md space-y-2">
              <div className="flex items-center gap-2">
                {authResult.authorized ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-600" />
                )}
                <span className="font-semibold">
                  {authResult.authorized ? 'AUTHORIZED' : 'BLOCKED'}
                </span>
              </div>
              <p className="text-sm"><strong>Risk Score:</strong> {authResult.risk_score?.toFixed(1) || 'N/A'}</p>
              <p className="text-sm"><strong>Reasoning:</strong> {authResult.reasoning}</p>
              <p className="text-xs text-muted-foreground">Action ID: {authResult.action_id}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Kill Switch */}
        <Card className="border-red-200 dark:border-red-900">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <Zap className="h-5 w-5" />
              Kill Switch
            </CardTitle>
            <CardDescription>Emergency — block all pending actions for this agent</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              variant="destructive"
              onClick={handleKill}
              disabled={loading === 'kill' || !agentId}
              className="w-full bg-red-600 hover:bg-red-700"
            >
              {loading === 'kill' ? 'Activating...' : '⚡ Activate Kill Switch'}
            </Button>

            {killResult && (
              <div className="mt-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-md text-sm">
                <p><strong>Agent:</strong> {killResult.agent_id}</p>
                <p><strong>Killed:</strong> {killResult.killed ? 'Yes' : 'No'}</p>
                <p><strong>Actions Blocked:</strong> {killResult.actions_blocked}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Action History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Action History
            </CardTitle>
            <CardDescription>View recent actions for this agent</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={handleHistory} disabled={loading === 'history' || !agentId}>
              {loading === 'history' ? 'Loading...' : 'Fetch History'}
            </Button>

            {history && (
              <div className="mt-2 space-y-2">
                <p className="text-sm font-semibold">Total: {history.total_actions} actions</p>
                <div className="max-h-60 overflow-y-auto space-y-2">
                  {history.actions?.map((a: any) => (
                    <div key={a.action_id} className="p-2 bg-muted rounded text-xs flex justify-between items-center">
                      <div>
                        <span className="font-mono">{a.action_type}</span>
                        <span className={`ml-2 ${a.authorized ? 'text-green-600' : 'text-red-600'}`}>
                          {a.authorized ? '✓' : '✗'}
                        </span>
                      </div>
                      <span className="text-muted-foreground">
                        Risk: {a.risk_score?.toFixed(1) || 'N/A'}
                      </span>
                    </div>
                  ))}
                  {history.actions?.length === 0 && (
                    <p className="text-sm text-muted-foreground">No actions recorded</p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
