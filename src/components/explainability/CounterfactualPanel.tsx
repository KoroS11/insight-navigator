import { HelpCircle, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

interface Counterfactual {
  id: string;
  question: string;
  outcome: string;
  impact: "reduced" | "unchanged" | "eliminated";
}

const counterfactuals: Counterfactual[] = [
  {
    id: "cf-1",
    question: "If this occurred during business hours?",
    outcome: "Flagged as 'Low Priority' (Policy #12 wouldn't trigger)",
    impact: "reduced",
  },
  {
    id: "cf-2",
    question: "If only 1 failed attempt occurred?",
    outcome: "Would not trigger alert (below threshold)",
    impact: "eliminated",
  },
  {
    id: "cf-3",
    question: "If from known IP range?",
    outcome: "Geographic rule wouldn't apply",
    impact: "reduced",
  },
];

const impactStyles = {
  reduced: "border-caution/30 bg-caution/5",
  unchanged: "border-border bg-card",
  eliminated: "border-success/30 bg-success/5",
};

export function CounterfactualPanel() {
  return (
    <div className="card-surface p-4">
      <h3 className="text-heading text-foreground mb-4 flex items-center gap-2">
        <HelpCircle className="w-5 h-5 text-info" />
        "What if..." Scenarios
      </h3>
      <p className="text-xs text-muted-foreground mb-4">
        Explore how different conditions would affect the detection outcome
      </p>

      <div className="space-y-3">
        {counterfactuals.map((cf, i) => (
          <motion.div
            key={cf.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`p-4 rounded-lg border ${impactStyles[cf.impact]}`}
          >
            <div className="flex items-start gap-2 mb-2">
              <span className="text-info">❓</span>
              <span className="text-sm font-medium text-foreground">
                {cf.question}
              </span>
            </div>
            <div className="flex items-start gap-2 pl-6">
              <ArrowRight className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
              <span className="text-sm text-muted-foreground">
                {cf.outcome}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
