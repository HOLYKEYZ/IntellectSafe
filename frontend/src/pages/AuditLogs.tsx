import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { getAuditLogs, AuditLog } from '@/lib/api'
import { format } from 'date-fns'

export default function AuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await getAuditLogs({ limit: 100 })
        setLogs(data)
      } catch (error) {
        console.error('Failed to fetch audit logs:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchLogs()
  }, [])

  if (loading) {
    return <div className="text-center py-8">Loading audit logs...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audit Logs</h1>
        <p className="text-muted-foreground">Immutable audit trail of all system actions</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {logs.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No audit logs found</p>
            ) : (
              logs.map((log) => (
                <div key={log.id} className="border-b pb-4 last:border-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="font-semibold">{log.action_type}</span>
                        <span className="text-sm text-muted-foreground">
                          {log.resource_type}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-1">{log.description}</p>
                      {log.actor && (
                        <p className="text-xs text-muted-foreground">Actor: {log.actor}</p>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {format(new Date(log.created_at), 'MMM dd, yyyy HH:mm:ss')}
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

