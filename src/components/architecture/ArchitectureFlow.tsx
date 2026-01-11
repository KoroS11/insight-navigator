import { Activity, Brain, Scale, MessageSquare, User } from "lucide-react";

interface PipelineStage {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  isHighlighted?: boolean;
}

interface Connection {
  from: string;
  to: string;
  label: string;
  type: "primary" | "feedback";
}

const stages: PipelineStage[] = [
  {
    id: "telemetry",
    title: "Telemetry Ingestion",
    description: "High-volume security event streams",
    icon: <Activity className="w-5 h-5" />,
  },
  {
    id: "neural",
    title: "Neural Signal Extraction",
    description: "Learned behavioral patterns",
    icon: <Brain className="w-5 h-5" />,
  },
  {
    id: "symbolic",
    title: "Symbolic Reasoning",
    description: "Policy-driven logic evaluation",
    icon: <Scale className="w-5 h-5" />,
  },
  {
    id: "explain",
    title: "Explainability",
    description: "Human-readable justifications",
    icon: <MessageSquare className="w-5 h-5" />,
    isHighlighted: true,
  },
  {
    id: "human",
    title: "Human Decision",
    description: "Analyst review and action",
    icon: <User className="w-5 h-5" />,
  },
];

const connections: Connection[] = [
  { from: "telemetry", to: "neural", label: "raw signals", type: "primary" },
  { from: "neural", to: "symbolic", label: "context", type: "primary" },
  { from: "symbolic", to: "explain", label: "constraints", type: "primary" },
  { from: "explain", to: "human", label: "justification", type: "primary" },
  { from: "neural", to: "explain", label: "patterns", type: "feedback" },
];

export function ArchitectureFlow() {
  return (
    <div className="w-full">
      {/* Pipeline Container */}
      <div className="relative bg-background rounded-xl border border-border/50 p-8 overflow-hidden">
        {/* Subtle background gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-muted/5 to-transparent pointer-events-none" />
        
        {/* Main horizontal pipeline */}
        <div className="relative flex items-center justify-between gap-4">
          {stages.map((stage, index) => (
            <div key={stage.id} className="flex items-center flex-1">
              {/* Stage Block */}
              <div
                className={`
                  relative flex-1 p-6 rounded-xl border transition-all duration-300
                  ${stage.isHighlighted 
                    ? "bg-primary/5 border-primary/30 shadow-[0_0_20px_rgba(14,165,233,0.08)]" 
                    : "bg-card border-border/50 hover:border-border"
                  }
                `}
              >
                {/* Icon */}
                <div className={`
                  w-10 h-10 rounded-lg flex items-center justify-center mb-4
                  ${stage.isHighlighted 
                    ? "bg-primary/10 text-primary" 
                    : "bg-muted/50 text-muted-foreground"
                  }
                `}>
                  {stage.icon}
                </div>
                
                {/* Title */}
                <h3 className={`
                  text-sm font-semibold mb-1
                  ${stage.isHighlighted ? "text-primary" : "text-foreground"}
                `}>
                  {stage.title}
                </h3>
                
                {/* Description */}
                <p className="text-xs text-muted-foreground">
                  {stage.description}
                </p>

                {/* Highlighted badge for Explainability */}
                {stage.isHighlighted && (
                  <div className="absolute -top-2 -right-2 px-2 py-0.5 bg-primary/20 text-primary text-[10px] font-medium rounded-full border border-primary/30">
                    Core
                  </div>
                )}
              </div>

              {/* Connection Arrow */}
              {index < stages.length - 1 && (
                <div className="flex flex-col items-center px-2 min-w-[60px]">
                  {/* Arrow line */}
                  <div className="w-full h-px bg-gradient-to-r from-border via-muted-foreground/30 to-border" />
                  {/* Arrow head */}
                  <svg width="8" height="6" viewBox="0 0 8 6" className="text-muted-foreground/50 -mt-[3px] ml-auto">
                    <path d="M4 6L8 0H0L4 6Z" fill="currentColor" />
                  </svg>
                  {/* Connection label */}
                  <span className="text-[10px] text-muted-foreground/70 mt-1 whitespace-nowrap">
                    {connections.find(c => c.from === stage.id)?.label}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Feedback loop indicator */}
        <div className="mt-8 pt-6 border-t border-border/30">
          <div className="flex items-center justify-center gap-8">
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <div className="w-8 h-px bg-gradient-to-r from-transparent to-muted-foreground/50" />
              <span>Primary flow</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <div className="w-8 h-px border-t border-dashed border-muted-foreground/50" />
              <span>Contextual feedback</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <div className="w-3 h-3 rounded-full border border-primary/50 bg-primary/10" />
              <span>Explainability (core differentiation)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key insight callout */}
      <div className="mt-6 p-4 rounded-lg bg-muted/30 border border-border/50">
        <p className="text-sm text-muted-foreground text-center">
          <span className="text-foreground font-medium">NSA-X assists.</span>
          {" "}Every recommendation includes its reasoning. Humans make the final decision.
        </p>
      </div>
    </div>
  );
}
