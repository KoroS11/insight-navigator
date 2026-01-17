import { MetricCard } from "@/components/shared/MetricCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Clock, AlertTriangle, Loader2 } from "lucide-react";
import { useEvents } from "@/hooks/use-events";
import { useAlerts, usePendingAlertCount } from "@/hooks/use-alerts";
import { useHealth } from "@/hooks/use-system";
import { Skeleton } from "@/components/ui/skeleton";

// Fallback for investigations (not yet an API endpoint)
const activeInvestigations = [
  { id: "INV-2026-0142", analyst: "j.chen", events: 3, started: "12:45" },
  { id: "INV-2026-0141", analyst: "m.rodriguez", events: 7, started: "11:20" },
];

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString('en-US', { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  });
}

function getEventSeverity(riskScore: number): 'high' | 'medium' | 'low' {
  if (riskScore >= 70) return 'high';
  if (riskScore >= 40) return 'medium';
  return 'low';
}

export default function Index() {
  const navigate = useNavigate();
  
  // Fetch data from API
  const { data: eventsData, isLoading: eventsLoading } = useEvents({ limit: 10 });
  const { data: alertsData, isLoading: alertsLoading } = useAlerts({ limit: 10 });
  const { data: pendingCount } = usePendingAlertCount();
  const { data: health } = useHealth();

  // Derive metrics
  const eventsProcessed = health?.metrics?.events_processed_24h ?? '-';
  const pendingReview = pendingCount ?? 0;
  return (
    <div className="p-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricCard
          label="Events Processed (24h)"
          value={typeof eventsProcessed === 'number' ? eventsProcessed.toLocaleString() : eventsProcessed}
          subValue="events"
          trend={{ direction: "up", value: "12%", label: "vs yesterday" }}
        />
        <MetricCard
          label="Median Analysis Time"
          value="340"
          subValue="ms"
          trend={{ direction: "down", value: "8%", label: "P95: 2.1s" }}
        />
        <MetricCard
          label="Pending Review"
          value={String(pendingReview)}
          subValue="alerts"
        />
        <MetricCard
          label="Active Investigations"
          value="2"
          subValue="analysts assigned"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Recent Alerts - 2/3 width */}
        <div className="col-span-2 card-surface">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h2 className="text-sm font-semibold">Recent Alerts</h2>
            <span className="text-xs text-muted-foreground">
              {alertsLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : `${alertsData?.total ?? 0} total`}
            </span>
          </div>
          
          <table className="data-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Event ID</th>
                <th>Classification</th>
                <th>Risk</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {alertsLoading ? (
                <tr>
                  <td colSpan={6} className="text-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto" />
                  </td>
                </tr>
              ) : alertsData?.alerts?.length ? (
                alertsData.alerts.map((alert) => (
                  <tr 
                    key={alert.id} 
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => navigate(`/alerts/${alert.id}`)}
                  >
                    <td>
                      <span className="font-mono text-xs text-primary">
                        {alert.id.slice(0, 8)}...
                      </span>
                    </td>
                    <td className="font-mono text-xs">
                      {alert.event_id ? `${alert.event_id.slice(0, 8)}...` : 'N/A'}
                    </td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        {alert.classification === "HIGH" && (
                          <AlertTriangle className="w-3 h-3 text-caution" />
                        )}
                        <span className="text-xs">{alert.classification}</span>
                      </div>
                    </td>
                    <td>
                      <span className={`font-mono text-xs ${
                        alert.composite_risk_score >= 70 ? 'text-destructive' : 
                        alert.composite_risk_score >= 40 ? 'text-caution' : ''
                      }`}>
                        {alert.composite_risk_score}
                      </span>
                    </td>
                    <td className="font-mono text-xs text-muted-foreground">
                      {formatTime(alert.created_at)}
                    </td>
                    <td>
                      <StatusBadge 
                        status={alert.status === 'PENDING' ? 'pending' : 'active'} 
                        label={alert.status} 
                      />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-muted-foreground">
                    No alerts found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Right Column */}
        <div className="space-y-4">
          {/* Active Investigations */}
          <div className="card-surface">
            <div className="p-4 border-b border-border">
              <h2 className="text-sm font-semibold">Active Investigations</h2>
            </div>
            <div className="p-4 space-y-3">
              {activeInvestigations.map((inv) => (
                <div key={inv.id} className="flex items-center justify-between text-sm">
                  <div>
                    <span className="font-mono text-xs text-foreground">{inv.id}</span>
                    <p className="text-xs text-muted-foreground">{inv.analyst} · {inv.events} events</p>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="w-3 h-3" />
                    <span>{inv.started}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="card-surface p-4">
            <h3 className="text-xs font-semibold mb-3">Today's Summary</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Benign</span>
                <span className="font-mono">1,542</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">False Positives</span>
                <span className="font-mono">218</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Under Review</span>
                <span className="font-mono text-caution">87</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-border">
                <span className="text-muted-foreground">Confirmed Threats</span>
                <span className="font-mono text-destructive">4</span>
              </div>
            </div>
          </div>

          {/* System Performance */}
          <div className="card-surface p-4">
            <h3 className="text-xs font-semibold mb-3">System Performance</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Throughput</span>
                <span className="font-mono">~4.2K events/min</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Queue Depth</span>
                <span className="font-mono">142</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Buffer Utilization</span>
                <span className="font-mono">23%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
