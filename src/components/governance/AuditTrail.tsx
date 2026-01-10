import { cn } from "@/lib/utils";
import { useState } from "react";
import { Search, Download, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AuditEntry {
  timestamp: string;
  actor: string;
  actorType: "system" | "analyst" | "admin";
  action: string;
  resource: string;
  result: "success" | "failure";
  eventId?: string;
}

const auditEntries: AuditEntry[] = [
  { 
    timestamp: "14:35:13.442", 
    actor: "NSA-X", 
    actorType: "system",
    action: "ALERT_SENT", 
    resource: "notification.slack.channel-security",
    result: "success",
    eventId: "EVT-2026-0847"
  },
  { 
    timestamp: "14:35:12.103", 
    actor: "j.chen", 
    actorType: "analyst",
    action: "ESCALATE", 
    resource: "EVT-2026-0847",
    result: "success"
  },
  { 
    timestamp: "14:32:45.887", 
    actor: "j.chen", 
    actorType: "analyst",
    action: "VIEW_EVENT", 
    resource: "EVT-2026-0847",
    result: "success"
  },
  { 
    timestamp: "14:32:23.009", 
    actor: "NSA-X", 
    actorType: "system",
    action: "EXPLANATION_GENERATED", 
    resource: "EVT-2026-0847",
    result: "success"
  },
  { 
    timestamp: "14:32:21.234", 
    actor: "NSA-X", 
    actorType: "system",
    action: "POLICY_EVALUATED", 
    resource: "rule.47, policy.12",
    result: "success"
  },
  { 
    timestamp: "14:32:18.442", 
    actor: "NSA-X", 
    actorType: "system",
    action: "EVENT_DETECTED", 
    resource: "netflow.anomaly.lateral_movement",
    result: "success",
    eventId: "EVT-2026-0847"
  },
];

const actorStyles = {
  system: "text-info",
  analyst: "text-success",
  admin: "text-caution",
};

export function AuditTrail() {
  const [filter, setFilter] = useState<string>("");

  return (
    <div className="card-surface">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">Audit Log</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Immutable record of all system and user actions
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
            <input 
              type="text"
              placeholder="Search..."
              className="h-8 w-48 pl-8 pr-3 text-xs bg-background border border-border rounded"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
          <Button variant="outline" size="sm" className="h-8 text-xs">
            <Filter className="w-3.5 h-3.5 mr-1.5" />
            Filter
          </Button>
          <Button variant="outline" size="sm" className="h-8 text-xs">
            <Download className="w-3.5 h-3.5 mr-1.5" />
            Export
          </Button>
        </div>
      </div>
      
      <table className="data-table">
        <thead>
          <tr>
            <th className="w-28">Timestamp</th>
            <th className="w-24">Actor</th>
            <th className="w-40">Action</th>
            <th>Resource</th>
            <th className="w-20 text-center">Result</th>
          </tr>
        </thead>
        <tbody>
          {auditEntries.map((entry, i) => (
            <tr key={i}>
              <td className="font-mono text-xs">{entry.timestamp}</td>
              <td>
                <span className={cn("text-xs font-medium", actorStyles[entry.actorType])}>
                  {entry.actor}
                </span>
              </td>
              <td className="font-mono text-xs">{entry.action}</td>
              <td className="font-mono text-xs text-muted-foreground truncate max-w-xs">
                {entry.resource}
              </td>
              <td className="text-center">
                <span className={cn(
                  "text-xs px-1.5 py-0.5 rounded",
                  entry.result === "success" ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"
                )}>
                  {entry.result}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
