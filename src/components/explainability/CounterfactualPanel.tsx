import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface Counterfactual {
  id: string;
  condition: string;
  outcome: string;
  impact: "eliminated" | "reduced" | "unchanged";
}

const counterfactuals: Counterfactual[] = [
  {
    id: "cf-1",
    condition: "Access during business hours (09:00-17:00)",
    outcome: "Policy #12 would not trigger, severity reduced to Low",
    impact: "reduced",
  },
  {
    id: "cf-2",
    condition: "Single failed login attempt (instead of 3)",
    outcome: "Alert would not be generated (below threshold)",
    impact: "eliminated",
  },
  {
    id: "cf-3",
    condition: "Connection to known corporate IP range",
    outcome: "Geographic anomaly rule would not apply",
    impact: "reduced",
  },
  {
    id: "cf-4",
    condition: "Regular user account (not service account)",
    outcome: "Different policy set applied, time restriction removed",
    impact: "reduced",
  },
];

const impactStyles = {
  eliminated: "border-l-success",
  reduced: "border-l-caution",
  unchanged: "border-l-muted-foreground",
};

const impactLabels = {
  eliminated: "No alert",
  reduced: "Lower severity",
  unchanged: "No change",
};

export function CounterfactualPanel() {
  return (
    <div className="card-surface">
      <div className="p-4 border-b border-border">
        <h3 className="text-sm font-semibold">Counterfactual Analysis</h3>
        <p className="text-xs text-muted-foreground mt-1">
          How would the outcome change under different conditions?
        </p>
      </div>

      <div className="p-4 space-y-3">
        {counterfactuals.map((cf) => (
          <div
            key={cf.id}
            className={cn(
              "p-3 border-l-2 bg-accent/20 rounded-r text-xs",
              impactStyles[cf.impact]
            )}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground">If:</span>
              <span className={cn(
                "px-1.5 py-0.5 rounded text-xs",
                cf.impact === "eliminated" ? "bg-success/10 text-success" : 
                cf.impact === "reduced" ? "bg-caution/10 text-caution" : 
                "bg-muted text-muted-foreground"
              )}>
                {impactLabels[cf.impact]}
              </span>
            </div>
            <p className="text-foreground mb-2">{cf.condition}</p>
            <div className="flex items-start gap-1.5 text-muted-foreground">
              <ArrowRight className="w-3 h-3 mt-0.5 flex-shrink-0" />
              <span>{cf.outcome}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
