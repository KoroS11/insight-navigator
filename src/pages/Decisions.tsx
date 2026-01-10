import { motion } from "framer-motion";
import { ConfidenceIndicator } from "@/components/decisions/ConfidenceIndicator";
import { ActionMatrix } from "@/components/decisions/ActionMatrix";
import { AnalystNotes } from "@/components/decisions/AnalystNotes";
import { UserCheck } from "lucide-react";

export default function Decisions() {
  return (
    <div className="min-h-screen p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-primary/10">
            <UserCheck className="w-5 h-5 text-primary" />
          </div>
          <h1 className="text-display text-foreground">Analyst Decision Panel</h1>
        </div>
        <p className="text-muted-foreground">
          Review system recommendations and make informed decisions
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <ConfidenceIndicator 
              level="moderate"
              reasoning="2 strong factors, 1 uncertain"
            />
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <ActionMatrix />
          </motion.div>
        </div>

        {/* Right Column */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <AnalystNotes />
          
          {/* Decision Guidance */}
          <div className="card-surface p-5 mt-6">
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Decision Guidance
            </h3>
            <div className="space-y-3 text-sm">
              <div className="p-3 rounded-lg bg-info/5 border border-info/20">
                <p className="text-info font-medium mb-1">When to Escalate</p>
                <p className="text-muted-foreground">
                  Multiple strong indicators present, unclear context, or potential high-impact threat.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-success/5 border border-success/20">
                <p className="text-success font-medium mb-1">When to Approve</p>
                <p className="text-muted-foreground">
                  Known pattern, verified user activity, or established exception.
                </p>
              </div>
              <div className="p-3 rounded-lg bg-muted border border-border">
                <p className="text-muted-foreground font-medium mb-1">When to Ignore</p>
                <p className="text-muted-foreground">
                  Confirmed false positive, testing activity, or duplicate alert.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
