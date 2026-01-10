import { Textarea } from "@/components/ui/textarea";
import { FileText, CheckCircle, ArrowUpCircle, XCircle } from "lucide-react";

interface PastDecision {
  action: "escalated" | "approved" | "ignored";
  outcome?: "confirmed" | "false_positive";
}

const pastDecisions: PastDecision[] = [
  { action: "escalated", outcome: "confirmed" },
  { action: "escalated", outcome: "confirmed" },
  { action: "escalated" },
  { action: "ignored", outcome: "false_positive" },
];

export function AnalystNotes() {
  const escalated = pastDecisions.filter(d => d.action === "escalated");
  const confirmed = escalated.filter(d => d.outcome === "confirmed");

  return (
    <div className="card-surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-4 h-4 text-muted-foreground" />
        <h3 className="text-sm font-medium text-foreground">
          Analyst Justification
        </h3>
      </div>

      <Textarea 
        placeholder="Required: Provide reasoning for your decision..."
        className="min-h-[100px] bg-background border-border resize-none mb-4"
      />

      <div className="pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground mb-3">
          Previous Decisions on Similar Events:
        </p>
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <ArrowUpCircle className="w-4 h-4 text-info" />
            <span className="text-foreground">
              {escalated.length} escalated
            </span>
            <span className="text-muted-foreground">
              ({confirmed.length} confirmed threats)
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <XCircle className="w-4 h-4 text-muted-foreground" />
            <span className="text-foreground">
              1 marked false positive
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
