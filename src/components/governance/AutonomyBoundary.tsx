import { Check, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

interface BoundaryItem {
  label: string;
  allowed: boolean;
}

const autonomousActions: BoundaryItem[] = [
  { label: "Detect anomalies", allowed: true },
  { label: "Generate explanations", allowed: true },
  { label: "Recommend actions", allowed: true },
  { label: "Log all decisions", allowed: true },
  { label: "Trigger notifications", allowed: true },
];

const humanRequiredActions: BoundaryItem[] = [
  { label: "Block network traffic", allowed: false },
  { label: "Isolate systems", allowed: false },
  { label: "Modify security policies", allowed: false },
  { label: "Terminate processes", allowed: false },
  { label: "Delete or quarantine files", allowed: false },
];

export function AutonomyBoundary() {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        className="card-surface p-5 border-success/20"
      >
        <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
          <Check className="w-5 h-5 text-success" />
          What NSA-X Can Do Autonomously
        </h3>
        <ul className="space-y-3">
          {autonomousActions.map((item, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex items-center gap-3 text-sm"
            >
              <div className="w-5 h-5 rounded-full bg-success/10 flex items-center justify-center">
                <Check className="w-3 h-3 text-success" />
              </div>
              <span className="text-foreground">{item.label}</span>
            </motion.li>
          ))}
        </ul>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="card-surface p-5 border-caution/20"
      >
        <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-caution" />
          What Requires Human Authority
        </h3>
        <ul className="space-y-3">
          {humanRequiredActions.map((item, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 + 0.1 }}
              className="flex items-center gap-3 text-sm"
            >
              <div className="w-5 h-5 rounded-full bg-caution/10 flex items-center justify-center">
                <AlertTriangle className="w-3 h-3 text-caution" />
              </div>
              <span className="text-foreground">{item.label}</span>
            </motion.li>
          ))}
        </ul>
      </motion.div>
    </div>
  );
}
