import { StatusBadge } from "@/components/shared/StatusBadge";
import { Clock, Network, User, MapPin } from "lucide-react";

interface EventData {
  id: string;
  timestamp: string;
  timestampMs: string;
  category: string;
  sourceIp: string;
  sourcePort: string;
  destIp: string;
  destPort: string;
  protocol: string;
  user: string;
  hostname: string;
  status: "pending" | "active" | "inactive";
}

const eventData: EventData = {
  id: "EVT-2026-01-10-0847-LM",
  timestamp: "2026-01-10",
  timestampMs: "14:32:18.442 UTC",
  category: "Lateral Movement Attempt",
  sourceIp: "10.42.17.89",
  sourcePort: "49152",
  destIp: "172.16.5.12",
  destPort: "443",
  protocol: "TCP/TLS",
  user: "svc_backup",
  hostname: "corp-ws-1247.internal.example.com",
  status: "pending",
};

export function EventSummary() {
  return (
    <div className="card-surface">
      <div className="flex items-center justify-between p-4 border-b border-border">
        <h3 className="text-sm font-semibold">Event Details</h3>
        <StatusBadge status={eventData.status} label="Awaiting Review" />
      </div>

      <div className="p-4 space-y-4">
        {/* Event ID */}
        <div>
          <p className="tech-label">Event ID</p>
          <p className="font-mono text-xs text-foreground">{eventData.id}</p>
        </div>

        {/* Timestamp */}
        <div className="flex items-start gap-2">
          <Clock className="w-3.5 h-3.5 text-muted-foreground mt-0.5" />
          <div>
            <p className="tech-label">Timestamp</p>
            <p className="font-mono text-xs text-foreground">{eventData.timestampMs}</p>
          </div>
        </div>

        {/* Network Info */}
        <div className="flex items-start gap-2">
          <Network className="w-3.5 h-3.5 text-muted-foreground mt-0.5" />
          <div className="flex-1">
            <p className="tech-label">Network</p>
            <div className="grid grid-cols-2 gap-2 mt-1">
              <div>
                <p className="text-xs text-muted-foreground">Source</p>
                <p className="font-mono text-xs">{eventData.sourceIp}:{eventData.sourcePort}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Destination</p>
                <p className="font-mono text-xs">{eventData.destIp}:{eventData.destPort}</p>
              </div>
            </div>
            <p className="font-mono text-xs text-muted-foreground mt-1">{eventData.protocol}</p>
          </div>
        </div>

        {/* User Context */}
        <div className="flex items-start gap-2">
          <User className="w-3.5 h-3.5 text-muted-foreground mt-0.5" />
          <div>
            <p className="tech-label">User</p>
            <p className="font-mono text-xs text-foreground">{eventData.user}</p>
            <p className="font-mono text-xs text-muted-foreground">{eventData.hostname}</p>
          </div>
        </div>

        {/* Category */}
        <div className="pt-3 border-t border-border">
          <p className="tech-label">Classification</p>
          <p className="text-sm text-caution font-medium mt-1">{eventData.category}</p>
        </div>
      </div>
    </div>
  );
}
