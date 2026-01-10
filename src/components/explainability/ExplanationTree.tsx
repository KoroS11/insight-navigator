import { useState } from "react";
import { ChevronRight, ChevronDown, AlertTriangle, Clock, MapPin, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface ExplanationNode {
  id: string;
  level: number;
  title: string;
  description?: string;
  confidence?: "high" | "moderate" | "low";
  icon?: React.ReactNode;
  children?: ExplanationNode[];
}

const explanationData: ExplanationNode = {
  id: "root",
  level: 1,
  title: "Why Flagged?",
  description: "Unusual authentication pattern detected",
  confidence: "high",
  icon: <AlertTriangle className="w-4 h-4" />,
  children: [
    {
      id: "factor-1",
      level: 2,
      title: "3 failed login attempts in 90 seconds",
      confidence: "high",
      icon: <Clock className="w-4 h-4" />,
    },
    {
      id: "factor-2",
      level: 2,
      title: "Access from new geographic location",
      confidence: "high",
      icon: <MapPin className="w-4 h-4" />,
    },
    {
      id: "factor-3",
      level: 2,
      title: "Service account used outside business hours",
      confidence: "moderate",
      icon: <User className="w-4 h-4" />,
      children: [
        {
          id: "rule-1",
          level: 3,
          title: "Rule #47: Geographic anomaly threshold",
          description: "Triggered when access originates from previously unseen location",
        },
        {
          id: "rule-2",
          level: 3,
          title: "Policy #12: Service account time restrictions",
          description: "Service accounts restricted to 08:00-18:00 UTC",
        },
      ],
    },
  ],
};

function TreeNode({ node, depth = 0 }: { node: ExplanationNode; depth?: number }) {
  const [isOpen, setIsOpen] = useState(depth < 2);
  const hasChildren = node.children && node.children.length > 0;

  const confidenceStyles = {
    high: "bg-success/10 text-success border-success/20",
    moderate: "bg-caution/10 text-caution border-caution/20",
    low: "bg-muted text-muted-foreground border-border",
  };

  return (
    <div className="relative">
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2, delay: depth * 0.05 }}
        className={cn(
          "flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all duration-200",
          "hover:bg-accent/50",
          depth > 0 && "ml-6 border-l-2 border-border"
        )}
        onClick={() => hasChildren && setIsOpen(!isOpen)}
      >
        {hasChildren && (
          <button className="mt-0.5 p-0.5 rounded hover:bg-accent">
            {isOpen ? (
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            )}
          </button>
        )}
        {!hasChildren && <div className="w-5" />}

        {node.icon && (
          <div className="mt-0.5 text-primary">{node.icon}</div>
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-foreground">
              {node.title}
            </span>
            {node.confidence && (
              <span className={cn(
                "px-2 py-0.5 rounded-full text-xs border",
                confidenceStyles[node.confidence]
              )}>
                {node.confidence} confidence
              </span>
            )}
          </div>
          {node.description && (
            <p className="text-xs text-muted-foreground mt-1">
              {node.description}
            </p>
          )}
        </div>
      </motion.div>

      <AnimatePresence>
        {isOpen && hasChildren && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {node.children!.map((child) => (
              <TreeNode key={child.id} node={child} depth={depth + 1} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function ExplanationTree() {
  return (
    <div className="card-surface p-4">
      <h3 className="text-heading text-foreground mb-4 flex items-center gap-2">
        <span className="text-lg">📊</span>
        Detection Reasoning
      </h3>
      <TreeNode node={explanationData} />
    </div>
  );
}
