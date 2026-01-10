import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface EvidenceNode {
  id: string;
  category: string;
  weight: "high" | "medium" | "low";
  items: {
    label: string;
    value: string;
    isAnomaly?: boolean;
  }[];
  children?: EvidenceNode[];
}

const evidenceData: EvidenceNode[] = [
  {
    id: "network",
    category: "Network Behavior",
    weight: "high",
    items: [
      { label: "Connections to non-standard port", value: "3 TCP connections to 8443", isAnomaly: true },
      { label: "Outbound traffic volume", value: "2.4MB in 90 sec", isAnomaly: true },
      { label: "Destination", value: "185.220.101.x (Tor exit node)", isAnomaly: true },
    ],
  },
  {
    id: "user",
    category: "User Context",
    weight: "medium",
    items: [
      { label: "Account type", value: "svc_backup (service account)" },
      { label: "Typical usage window", value: "09:00-17:00 EST" },
      { label: "Current access time", value: "02:32 EST", isAnomaly: true },
    ],
  },
  {
    id: "historical",
    category: "Historical Patterns",
    weight: "low",
    items: [
      { label: "Similar pattern", value: "Q3 2024 incident (INV-2024-0891)" },
      { label: "Outcome", value: "Confirmed credential compromise" },
    ],
  },
  {
    id: "rules",
    category: "Rules Applied",
    weight: "medium",
    items: [
      { label: "Rule #47", value: "Geographic anomaly threshold triggered" },
      { label: "Policy #12", value: "Service account time restrictions violated" },
    ],
  },
];

const weightColors = {
  high: "text-foreground",
  medium: "text-muted-foreground",
  low: "text-muted-foreground/70",
};

const weightLabels = {
  high: "High",
  medium: "Med",
  low: "Low",
};

function EvidenceSection({ node }: { node: EvidenceNode }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="border-b border-border last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 text-left hover:bg-accent/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />
          )}
          <span className={cn("text-sm font-medium", weightColors[node.weight])}>
            {node.category}
          </span>
        </div>
        <span className={cn(
          "text-xs px-1.5 py-0.5 rounded",
          node.weight === "high" ? "bg-info/10 text-info" : "bg-muted text-muted-foreground"
        )}>
          Weight: {weightLabels[node.weight]}
        </span>
      </button>

      {isOpen && (
        <div className="px-3 pb-3 space-y-2">
          {node.items.map((item, i) => (
            <div key={i} className="flex items-start gap-2 pl-5">
              <span className="text-xs text-muted-foreground w-36 flex-shrink-0">{item.label}</span>
              <span className={cn(
                "text-xs font-mono",
                item.isAnomaly ? "text-caution" : "text-foreground"
              )}>
                {item.value}
                {item.isAnomaly && " ⚠"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function ExplanationTree() {
  return (
    <div className="card-surface">
      <div className="p-4 border-b border-border">
        <h3 className="text-sm font-semibold">Detection Factors</h3>
        <p className="text-xs text-muted-foreground mt-1">
          Evidence contributing to this detection, ordered by weight
        </p>
      </div>

      <div>
        {evidenceData.map((node) => (
          <EvidenceSection key={node.id} node={node} />
        ))}
      </div>
    </div>
  );
}
