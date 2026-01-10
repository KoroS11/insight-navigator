import { Button } from "@/components/ui/button";
import { CheckCircle, ArrowUpCircle, XCircle } from "lucide-react";
import { motion } from "framer-motion";

interface Action {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  variant: "success" | "action" | "outline";
  recommended?: boolean;
}

const actions: Action[] = [
  {
    id: "approve",
    label: "APPROVE",
    description: "Mark as safe, add to allow list",
    icon: <CheckCircle className="w-5 h-5" />,
    variant: "success",
  },
  {
    id: "escalate",
    label: "ESCALATE",
    description: "Send to L2 analyst for deep dive",
    icon: <ArrowUpCircle className="w-5 h-5" />,
    variant: "action",
    recommended: true,
  },
  {
    id: "ignore",
    label: "IGNORE",
    description: "Suppress as false positive",
    icon: <XCircle className="w-5 h-5" />,
    variant: "outline",
  },
];

export function ActionMatrix() {
  return (
    <div className="card-surface p-5">
      <div className="mb-4">
        <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
          Recommended Action
        </p>
        <p className="text-lg font-semibold text-info">ESCALATE TO TIER 2</p>
      </div>

      <p className="text-sm text-muted-foreground mb-4">
        Alternative Actions Available:
      </p>

      <div className="grid grid-cols-3 gap-3">
        {actions.map((action, i) => (
          <motion.div
            key={action.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="relative"
          >
            {action.recommended && (
              <span className="absolute -top-2 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-info text-info-foreground text-[10px] rounded-full font-medium">
                Recommended
              </span>
            )}
            <div className={`p-4 rounded-lg border ${
              action.recommended 
                ? "border-info/30 bg-info/5" 
                : "border-border bg-card"
            }`}>
              <div className="flex flex-col items-center text-center gap-2">
                <div className={`${
                  action.variant === "success" ? "text-success" :
                  action.variant === "action" ? "text-info" :
                  "text-muted-foreground"
                }`}>
                  {action.icon}
                </div>
                <p className="text-sm font-semibold text-foreground">
                  {action.label}
                </p>
                <p className="text-xs text-muted-foreground">
                  {action.description}
                </p>
                <Button 
                  variant={action.variant}
                  size="sm" 
                  className="w-full mt-2"
                >
                  Select
                </Button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
