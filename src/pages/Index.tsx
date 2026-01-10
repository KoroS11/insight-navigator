import { MetricCard } from "@/components/shared/MetricCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Link } from "react-router-dom";
import { ArrowRight, Clock, AlertTriangle } from "lucide-react";

const recentEvents = [
  {
    id: "EVT-2026-01-10-0847-LM",
    source: "10.42.17.89",
    destination: "172.16.5.12:443",
    type: "Lateral Movement",
    severity: "high",
    time: "14:35:42.103",
    status: "pending" as const,
  },
  {
    id: "EVT-2026-01-10-0846-PE",
    source: "10.42.18.204",
    destination: "192.168.1.1:22",
    type: "Privilege Escalation",
    severity: "medium",
    time: "14:32:18.887",
    status: "pending" as const,
  },
  {
    id: "EVT-2026-01-10-0845-DE",
    source: "10.42.12.55",
    destination: "185.220.101.42:8443",
    type: "Data Exfiltration",
    severity: "high",
    time: "14:28:03.442",
    status: "active" as const,
  },
];

const activeInvestigations = [
  { id: "INV-2026-0142", analyst: "j.chen", events: 3, started: "12:45" },
  { id: "INV-2026-0141", analyst: "m.rodriguez", events: 7, started: "11:20" },
];

export default function Index() {
  return (
    <div className="p-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricCard
          label="Events Processed (24h)"
          value="1,847"
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
          value="3"
          subValue="events"
        />
        <MetricCard
          label="Active Investigations"
          value="2"
          subValue="analysts assigned"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Recent Events - 2/3 width */}
        <div className="col-span-2 card-surface">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h2 className="text-sm font-semibold">Recent Events</h2>
            <Link 
              to="/explainability" 
              className="flex items-center gap-1 text-xs text-primary hover:underline"
            >
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          
          <table className="data-table">
            <thead>
              <tr>
                <th>Event ID</th>
                <th>Source</th>
                <th>Destination</th>
                <th>Type</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentEvents.map((event) => (
                <tr key={event.id}>
                  <td>
                    <Link 
                      to="/explainability" 
                      className="font-mono text-xs text-primary hover:underline"
                    >
                      {event.id}
                    </Link>
                  </td>
                  <td className="font-mono text-xs">{event.source}</td>
                  <td className="font-mono text-xs">{event.destination}</td>
                  <td>
                    <div className="flex items-center gap-1.5">
                      {event.severity === "high" && (
                        <AlertTriangle className="w-3 h-3 text-caution" />
                      )}
                      <span className="text-xs">{event.type}</span>
                    </div>
                  </td>
                  <td className="font-mono text-xs text-muted-foreground">{event.time}</td>
                  <td>
                    <StatusBadge status={event.status} label={event.status === "pending" ? "Pending" : "In Progress"} />
                  </td>
                </tr>
              ))}
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
