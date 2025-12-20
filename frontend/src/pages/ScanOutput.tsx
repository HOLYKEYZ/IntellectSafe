import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { scanOutput, ScanResponse } from '@/lib/api'

export default function ScanOutput() {
  const [output, setOutput] = useState('')
  const [originalPrompt, setOriginalPrompt] = useState('')
  const [result, setResult] = useState<ScanResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleScan = async () => {
    if (!output.trim()) return

    setLoading(true)
    try {
      const response = await scanOutput({
        output,
        original_prompt: originalPrompt || undefined,
      })
      setResult(response)
    } catch (error) {
      console.error('Scan failed:', error)
      alert('Scan failed. Please check your API connection.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Scan Output</h1>
        <p className="text-muted-foreground">Analyze LLM outputs for safety issues</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Enter Output</CardTitle>
          <CardDescription>Paste the LLM output to scan for safety issues</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Original Prompt (Optional)</label>
            <textarea
              value={originalPrompt}
              onChange={(e) => setOriginalPrompt(e.target.value)}
              placeholder="Enter original prompt (optional)..."
              className="w-full min-h-[100px] p-4 border rounded-md font-mono text-sm"
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-2 block">LLM Output</label>
            <textarea
              value={output}
              onChange={(e) => setOutput(e.target.value)}
              placeholder="Enter LLM output to scan..."
              className="w-full min-h-[200px] p-4 border rounded-md font-mono text-sm"
            />
          </div>
          <Button onClick={handleScan} disabled={loading || !output.trim()}>
            {loading ? 'Scanning...' : 'Scan Output'}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Scan Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Verdict</p>
                <p className="text-lg font-semibold capitalize">{result.verdict}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Risk Score</p>
                <p className="text-lg font-semibold">{result.risk_score.toFixed(1)} / 100</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-2">Explanation</p>
              <p className="text-sm whitespace-pre-wrap bg-muted p-4 rounded-md">
                {result.explanation}
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

