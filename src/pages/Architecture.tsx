import { useState } from "react";
import { ArchitectureFlow } from "@/components/architecture/ArchitectureFlow";
import { ChevronDown, ChevronRight, Check, AlertCircle } from "lucide-react";

interface LayerCard {
  id: string;
  name: string;
  purpose: string;
  strength: string;
  limitation: string;
}

const layers: LayerCard[] = [
  {
    id: "neural",
    name: "Neural Signal Extraction",
    purpose: "Identifies unusual behavior patterns from network telemetry",
    strength: "Detects novel threats without pre-defined signatures",
    limitation: "Cannot explain its own decisions",
  },
  {
    id: "symbolic",
    name: "Symbolic Reasoning",
    purpose: "Applies organizational policies and security rules",
    strength: "Provides interpretable, auditable decision logic",
    limitation: "Requires neural layer for pattern discovery",
  },
  {
    id: "explain",
    name: "Explainability Engine",
    purpose: "Generates human-readable justifications for each alert",
    strength: "Bridges AI decisions to analyst understanding",
    limitation: "Depth depends on symbolic rule coverage",
  },
  {
    id: "response",
    name: "Response Orchestration",
    purpose: "Recommends actions based on threat context and policy",
    strength: "Integrates with existing security workflows",
    limitation: "Blocking actions require human approval",
  },
];

export default function Architecture() {
  const [expandedLayer, setExpandedLayer] = useState<string | null>(null);

  const toggleLayer = (id: string) => {
    setExpandedLayer(expandedLayer === id ? null : id);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-foreground mb-2">
          System Architecture
        </h1>
        <p className="text-sm text-muted-foreground">
          A neuro-symbolic reasoning pipeline that explains its decisions
        </p>
      </div>

      {/* Architecture Diagram */}
      <div className="mb-10">
        <ArchitectureFlow />
      </div>

      {/* Layer Details - Expandable Cards */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-foreground mb-4">
          Layer Overview
        </h2>
        <div className="space-y-2">
          {layers.map((layer) => (
            <div
              key={layer.id}
              className="rounded-lg border border-border/50 bg-card overflow-hidden transition-all duration-200"
            >
              {/* Header - Always visible */}
              <button
                onClick={() => toggleLayer(layer.id)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-foreground">
                    {layer.name}
                  </span>
                </div>
                {expandedLayer === layer.id ? (
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                )}
              </button>

              {/* Expanded Content */}
              {expandedLayer === layer.id && (
                <div className="px-4 pb-4 space-y-3 border-t border-border/30">
                  <div className="pt-3">
                    <p className="text-xs text-muted-foreground mb-3">
                      {layer.purpose}
                    </p>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-start gap-2">
                        <Check className="w-3.5 h-3.5 text-emerald-500 mt-0.5 shrink-0" />
                        <div>
                          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                            Strength
                          </span>
                          <p className="text-xs text-foreground">
                            {layer.strength}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-2">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
                        <div>
                          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                            Limitation
                          </span>
                          <p className="text-xs text-foreground">
                            {layer.limitation}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Design Principles */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 rounded-lg bg-muted/20 border border-border/30">
          <h3 className="text-xs font-semibold text-foreground mb-2">
            Transparency First
          </h3>
          <p className="text-xs text-muted-foreground">
            Every alert includes a complete reasoning chain that analysts can verify and question.
          </p>
        </div>

        <div className="p-4 rounded-lg bg-muted/20 border border-border/30">
          <h3 className="text-xs font-semibold text-foreground mb-2">
            Human Authority
          </h3>
          <p className="text-xs text-muted-foreground">
            Blocking and remediation actions are never automated. Analysts retain full control.
          </p>
        </div>

        <div className="p-4 rounded-lg bg-muted/20 border border-border/30">
          <h3 className="text-xs font-semibold text-foreground mb-2">
            Graceful Uncertainty
          </h3>
          <p className="text-xs text-muted-foreground">
            When confidence is low, the system clearly communicates what it doesn't know.
          </p>
        </div>
      </div>
    </div>
  );
}
