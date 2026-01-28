import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { getRiskReport, getSafetyScore } from '@/lib/api'

export default function Reports() {
  const [days, setDays] = useState(7)
  const [report, setReport] = useState<any>(null)
  const [safetyScore, setSafetyScore] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const fetchReport = async () => {
    setLoading(true)
    try {
      const [riskReport, score] = await Promise.all([
        getRiskReport(days),
        getSafetyScore(days),
      ])
      setReport(riskReport)
      setSafetyScore(score)
    } catch (error) {
      console.error('Failed to fetch report:', error)
      alert('Failed to fetch report. Please check your API connection.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Reports</h1>
        <p className="text-muted-foreground">Generate risk and safety reports</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Generate Report</CardTitle>
          <CardDescription>Select time period and generate comprehensive safety report</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Days</label>
            <input
              type="number"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              min={1}
              max={365}
              className="w-full p-2 border rounded-md bg-background text-foreground"
            />
          </div>
          <Button onClick={fetchReport} disabled={loading}>
            {loading ? 'Generating...' : 'Generate Report'}
          </Button>
        </CardContent>
      </Card>

      {report && safetyScore && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Safety Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold mb-2">
                {safetyScore.safety_score.toFixed(1)}
              </div>
              <p className="text-muted-foreground">
                Confidence: {(safetyScore.confidence * 100).toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Risk Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Total Scans</p>
                  <p className="text-2xl font-bold">{report.summary.total_scans}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Average Risk Score</p>
                  <p className="text-2xl font-bold">
                    {report.summary.average_risk_score.toFixed(1)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">High Risk Count</p>
                  <p className="text-2xl font-bold text-red-600">
                    {report.summary.high_risk_count}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Max Risk Score</p>
                  <p className="text-2xl font-bold">
                    {report.summary.max_risk_score.toFixed(1)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {report.risk_distribution && (
            <Card>
              <CardHeader>
                <CardTitle>Risk Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(report.risk_distribution).map(([level, count]: [string, any]) => (
                    <div key={level} className="flex items-center justify-between">
                      <span className="capitalize font-medium">{level}</span>
                      <span>{count}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

