import { StatusBadge } from "@/components/shared/StatusBadge";
import { Clock, Tag, Hash, AlertCircle } from "lucide-react";

interface EventData {
  id: string;
  timestamp: string;
  category: string;
  detectionMethod: string;
  status: "pending" | "active" | "inactive";
}

const eventData: EventData = {
  id: "EVT-2024-0842",
  timestamp: "14:32:18 UTC",
  category: "Lateral Movement Attempt",
  detectionMethod: "Neural anomaly score",
  status: "pending",
};

export function EventSummary() {
  return (
    <div className="card-surface p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-heading text-foreground">Event Summary</h3>
        <StatusBadge status={eventData.status} label="Awaiting Review" pulse />
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Hash className="w-4 h-4 text-primary" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Event ID</p>
            <p className="text-sm font-mono text-foreground">{eventData.id}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Clock className="w-4 h-4 text-primary" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Timestamp</p>
            <p className="text-sm font-mono text-foreground">{eventData.timestamp}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-caution/10">
            <Tag className="w-4 h-4 text-caution" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Category</p>
            <p className="text-sm text-foreground">{eventData.category}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-info/10">
            <AlertCircle className="w-4 h-4 text-info" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Initial Detection</p>
            <p className="text-sm text-foreground">{eventData.detectionMethod}</p>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground italic">
          (Illustrative data for demonstration purposes)
        </p>
      </div>
    </div>
  );
}
