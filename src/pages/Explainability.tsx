import { motion } from "framer-motion";
import { EventSummary } from "@/components/explainability/EventSummary";
import { ExplanationTree } from "@/components/explainability/ExplanationTree";
import { CounterfactualPanel } from "@/components/explainability/CounterfactualPanel";
import { Brain } from "lucide-react";

export default function Explainability() {
  return (
    <div className="min-h-screen p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-primary/10">
            <Brain className="w-5 h-5 text-primary" />
          </div>
          <h1 className="text-display text-foreground">Explainability View</h1>
        </div>
        <p className="text-muted-foreground">
          Deep-dive into detection reasoning with counterfactual analysis
        </p>
      </motion.div>

      {/* Multi-Panel Layout */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left: Event Summary */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <EventSummary />
        </motion.div>

        {/* Center: Explanation Tree */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <ExplanationTree />
        </motion.div>

        {/* Right: Counterfactuals */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <CounterfactualPanel />
        </motion.div>
      </div>

      {/* Evidence Strength */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mt-8"
      >
        <div className="card-surface p-6">
          <h3 className="text-heading text-foreground mb-4">
            Evidence Strength Distribution
          </h3>
          <p className="text-xs text-muted-foreground mb-4">
            Relative importance of each contributing factor
          </p>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-foreground">Failed Login Attempts</span>
                <span className="text-muted-foreground">Strong</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "85%" }}
                  transition={{ delay: 0.5, duration: 0.5 }}
                  className="h-full bg-info rounded-full"
                />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-foreground">Geographic Anomaly</span>
                <span className="text-muted-foreground">Strong</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "75%" }}
                  transition={{ delay: 0.6, duration: 0.5 }}
                  className="h-full bg-info rounded-full"
                />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-foreground">Time-Based Rule</span>
                <span className="text-muted-foreground">Moderate</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "55%" }}
                  transition={{ delay: 0.7, duration: 0.5 }}
                  className="h-full bg-caution rounded-full"
                />
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
