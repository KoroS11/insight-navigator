import { Clock, Eye, ArrowUpCircle, Bell, Brain, Cpu, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

interface AuditEntry {
  timestamp: string;
  action: string;
  icon: React.ReactNode;
  type: "system" | "human" | "notification";
}

const auditEntries: AuditEntry[] = [
  { timestamp: "14:32:18", action: "Event detected (EVT-0842)", icon: <AlertCircle className="w-4 h-4" />, type: "system" },
  { timestamp: "14:32:19", action: "Neural analysis completed", icon: <Cpu className="w-4 h-4" />, type: "system" },
  { timestamp: "14:32:21", action: "Symbolic reasoning applied", icon: <Brain className="w-4 h-4" />, type: "system" },
  { timestamp: "14:32:23", action: "Explanation generated", icon: <Brain className="w-4 h-4" />, type: "system" },
  { timestamp: "14:32:45", action: "Analyst viewed event", icon: <Eye className="w-4 h-4" />, type: "human" },
  { timestamp: "14:35:12", action: "Analyst escalated to Tier 2", icon: <ArrowUpCircle className="w-4 h-4" />, type: "human" },
  { timestamp: "14:35:13", action: "Notification sent", icon: <Bell className="w-4 h-4" />, type: "notification" },
];

const typeStyles = {
  system: "border-info/30 bg-info/5",
  human: "border-success/30 bg-success/5",
  notification: "border-caution/30 bg-caution/5",
};

const iconStyles = {
  system: "text-info",
  human: "text-success",
  notification: "text-caution",
};

export function AuditTrail() {
  return (
    <div className="card-surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <Clock className="w-5 h-5 text-muted-foreground" />
        <h3 className="text-sm font-semibold text-foreground">
          Recent System Actions
        </h3>
        <span className="text-xs text-muted-foreground">(Illustrative Timeline)</span>
      </div>

      <div className="space-y-2">
        {auditEntries.map((entry, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className={`flex items-center gap-3 p-3 rounded-lg border ${typeStyles[entry.type]}`}
          >
            <span className="text-xs font-mono text-muted-foreground w-16">
              {entry.timestamp}
            </span>
            <div className={iconStyles[entry.type]}>
              {entry.icon}
            </div>
            <span className="text-sm text-foreground">
              {entry.action}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
