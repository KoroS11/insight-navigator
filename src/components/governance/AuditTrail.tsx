import { cn } from "@/lib/utils";
import { useState } from "react";
import { Search, Download, Filter, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuditLog } from "@/hooks/use-audit";

interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  actorType: "system" | "analyst" | "admin";
  action: string;
  resource: string;
  result: "success" | "failure";
  eventId?: string;
}

const actorStyles = {
  system: "text-info",
  analyst: "text-success",
  admin: "text-caution",
};

function getActorType(actor: string): "system" | "analyst" | "admin" {
  if (actor === "NSA-X" || actor === "system") return "system";
  if (actor === "admin" || actor.toLowerCase().includes("admin")) return "admin";
  return "analyst";
}

function formatTimestamp(ts: string): string {
  const date = new Date(ts);
  const dateStr = date.toLocaleDateString('en-US', { 
    month: '2-digit', 
    day: '2-digit',
    year: '2-digit'
  });
  const timeStr = date.toLocaleTimeString('en-US', { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  });
  return `${dateStr} ${timeStr}`;
}

export function AuditTrail() {
  const [filter, setFilter] = useState<string>("");
  const { data: auditData, isLoading, error } = useAuditLog({ limit: 50 });

  // Transform API data to component format
  const auditEntries: AuditEntry[] = auditData?.entries?.map(entry => ({
    id: entry.id,
    timestamp: formatTimestamp(entry.timestamp),
    actor: entry.actor,
    actorType: getActorType(entry.actor),
    action: entry.action,
    resource: entry.resource_type ? `${entry.resource_type}${entry.resource_id ? '.' + entry.resource_id : ''}` : entry.action,
    result: entry.result === 'success' ? 'success' : 'failure',
    eventId: entry.resource_type === 'event' ? entry.resource_id || undefined : undefined,
  })) || [];

  // Filter entries by search term
  const filteredEntries = filter 
    ? auditEntries.filter(e => 
        e.action.toLowerCase().includes(filter.toLowerCase()) ||
        e.actor.toLowerCase().includes(filter.toLowerCase()) ||
        e.resource.toLowerCase().includes(filter.toLowerCase())
      )
    : auditEntries;

  return (
    <div className="card-surface">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">Audit Log</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Immutable record of all system and user actions
            {auditData?.total !== undefined && ` (${auditData.total} entries)`}
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
          {isLoading ? (
            <tr>
              <td colSpan={5} className="text-center py-8">
                <Loader2 className="w-6 h-6 animate-spin mx-auto" />
              </td>
            </tr>
          ) : error ? (
            <tr>
              <td colSpan={5} className="text-center py-8 text-destructive">
                Failed to load audit log
              </td>
            </tr>
          ) : filteredEntries.length === 0 ? (
            <tr>
              <td colSpan={5} className="text-center py-8 text-muted-foreground">
                No audit entries found
              </td>
            </tr>
          ) : (
            filteredEntries.map((entry) => (
              <tr key={entry.id}>
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
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
