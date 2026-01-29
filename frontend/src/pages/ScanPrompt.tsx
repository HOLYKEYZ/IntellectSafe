import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { scanPrompt, ScanResponse } from '@/lib/api'
import { AlertCircle, CheckCircle, XCircle, Flag } from 'lucide-react'

export default function ScanPrompt() {
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState<ScanResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleScan = async () => {
    if (!prompt.trim()) return

    setLoading(true)
    try {
      const response = await scanPrompt({ prompt })
      setResult(response)
    } catch (error) {
      console.error('Scan failed:', error)
      alert('Scan failed. Please check your API connection.')
    } finally {
      setLoading(false)
    }
  }

  const getVerdictIcon = (verdict: string) => {
    switch (verdict) {
      case 'blocked': return <XCircle className="h-5 w-5 text-red-600" />
      case 'flagged': return <Flag className="h-5 w-5 text-yellow-600" />
      case 'allowed': return <CheckCircle className="h-5 w-5 text-green-600" />
      default: return <AlertCircle className="h-5 w-5 text-gray-600" />
    }
  }

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-red-600'
    if (score >= 60) return 'text-orange-600'
    if (score >= 40) return 'text-yellow-600'
    return 'text-green-600'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Scan Prompt</h1>
        <p className="text-muted-foreground">Detect prompt injection and manipulation attempts</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Enter Prompt</CardTitle>
          <CardDescription>Paste the prompt you want to scan for security risks</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter prompt to scan..."
            className="w-full min-h-[200px] p-4 border rounded-md font-mono text-sm bg-background text-foreground"
          />
          <Button onClick={handleScan} disabled={loading || !prompt.trim()}>
            {loading ? 'Scanning...' : 'Scan Prompt'}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              {getVerdictIcon(result.verdict)}
              <span>Scan Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Verdict</p>
                <p className="text-lg font-semibold capitalize">{result.verdict}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Risk Score</p>
                <p className={`text-lg font-semibold ${getRiskColor(result.risk_score)}`}>
                  {result.risk_score.toFixed(1)} / 100
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Risk Level</p>
                <p className="text-lg font-semibold capitalize">{result.risk_level}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Confidence</p>
                <p className="text-lg font-semibold">
                  {(result.confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            <div>
              <p className="text-sm text-muted-foreground mb-2">Explanation</p>
              <p className="text-sm whitespace-pre-wrap bg-muted p-4 rounded-md">
                {result.explanation}
              </p>
            </div>

            {result.signals && Object.keys(result.signals).length > 0 && (
              <div>
                <p className="text-sm text-muted-foreground mb-2">Signals Detected</p>
                <pre className="text-xs bg-muted p-4 rounded-md overflow-auto">
                  {JSON.stringify(result.signals, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

