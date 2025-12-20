import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { getRiskScores, RiskScore } from '@/lib/api'
import { format } from 'date-fns'

export default function RiskScores() {
  const [scores, setScores] = useState<RiskScore[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchScores = async () => {
      try {
        const data = await getRiskScores({ limit: 100 })
        setScores(data)
      } catch (error) {
        console.error('Failed to fetch risk scores:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchScores()
  }, [])

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-red-600 bg-red-50'
    if (score >= 60) return 'text-orange-600 bg-orange-50'
    if (score >= 40) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  if (loading) {
    return <div className="text-center py-8">Loading risk scores...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Risk Scores</h1>
        <p className="text-muted-foreground">Historical risk assessments</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Risk Scores</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {scores.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No risk scores found</p>
            ) : (
              scores.map((score) => (
                <div key={score.id} className="border-b pb-4 last:border-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="font-semibold capitalize">{score.module_type.replace('_', ' ')}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(score.risk_score)}`}>
                          {score.risk_score.toFixed(1)}
                        </span>
                        <span className="text-sm text-muted-foreground capitalize">
                          {score.risk_level}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-1">{score.explanation}</p>
                      <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                        <span>Verdict: {score.verdict}</span>
                        <span>Confidence: {(score.confidence * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {format(new Date(score.created_at), 'MMM dd, yyyy HH:mm:ss')}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

