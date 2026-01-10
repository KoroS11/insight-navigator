import { Textarea } from "@/components/ui/textarea";
import { ArrowUpCircle, Check, X, Clock } from "lucide-react";

const pastDecisions = [
  { 
    id: "EVT-2024-0791", 
    action: "Escalated", 
    outcome: "Confirmed threat", 
    resolution: "8h",
    correct: true 
  },
  { 
    id: "EVT-2024-0654", 
    action: "False positive", 
    outcome: "User error", 
    resolution: "Closed",
    correct: true 
  },
  { 
    id: "EVT-2024-0502", 
    action: "Escalated", 
    outcome: "Benign anomaly", 
    resolution: "2h",
    correct: false 
  },
];

export function AnalystNotes() {
  return (
    <div className="card-surface">
      <div className="p-4 border-b border-border">
        <h3 className="text-sm font-semibold">Decision Log</h3>
      </div>

      <div className="p-4 space-y-4">
        {/* Justification */}
        <div>
          <label className="text-xs text-muted-foreground mb-2 block">
            Justification <span className="text-caution">*</span>
          </label>
          <Textarea 
            placeholder="Provide reasoning for your decision..."
            className="min-h-[80px] bg-background border-border resize-none text-sm"
          />
        </div>

        {/* Structured Fields */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-muted-foreground mb-1.5 block">
              Confidence in decision
            </label>
            <select className="w-full h-9 px-3 text-xs bg-background border border-border rounded">
              <option>High</option>
              <option>Medium</option>
              <option>Low - need more context</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-muted-foreground mb-1.5 block">
              Follow-up required?
            </label>
            <select className="w-full h-9 px-3 text-xs bg-background border border-border rounded">
              <option>No</option>
              <option>Yes - within 24h</option>
              <option>Yes - within 1 week</option>
            </select>
          </div>
        </div>
      </div>

      {/* Past Decisions */}
      <div className="border-t border-border">
        <div className="p-4">
          <p className="text-xs text-muted-foreground mb-3">
            Previous decisions on similar events:
          </p>
          <div className="space-y-2">
            {pastDecisions.map((decision) => (
              <div 
                key={decision.id} 
                className="flex items-center justify-between text-xs p-2 bg-accent/20 rounded"
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-muted-foreground">{decision.id}</span>
                  <span className="text-foreground">{decision.action}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-muted-foreground">{decision.outcome}</span>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3 text-muted-foreground" />
                    <span className="text-muted-foreground">{decision.resolution}</span>
                  </div>
                  {decision.correct ? (
                    <Check className="w-3.5 h-3.5 text-success" />
                  ) : (
                    <X className="w-3.5 h-3.5 text-muted-foreground" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
