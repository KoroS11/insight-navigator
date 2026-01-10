import { motion } from "framer-motion";
import { ArchitectureFlow } from "@/components/architecture/ArchitectureFlow";
import { Brain, Cpu, Shield, AlertCircle, Zap, Eye } from "lucide-react";

interface LayerCard {
  id: string;
  name: string;
  icon: React.ReactNode;
  function: string;
  whyExists: string;
  limitation: string;
  feedsInto: string;
}

const layers: LayerCard[] = [
  {
    id: "neural",
    name: "Neural Detection Layer",
    icon: <Cpu className="w-6 h-6" />,
    function: "Pattern recognition from network telemetry",
    whyExists: "Detects anomalies humans would miss",
    limitation: "Cannot explain its own decisions",
    feedsInto: "Symbolic Reasoning Layer",
  },
  {
    id: "symbolic",
    name: "Symbolic Reasoning Layer",
    icon: <Brain className="w-6 h-6" />,
    function: "Rule-based analysis and policy matching",
    whyExists: "Provides logical structure to detections",
    limitation: "Requires neural input for novel patterns",
    feedsInto: "Explanation Engine",
  },
  {
    id: "explain",
    name: "Explanation Engine",
    icon: <Eye className="w-6 h-6" />,
    function: "Generates human-readable reasoning chains",
    whyExists: "Enables audit and trust verification",
    limitation: "Explanation depth limited by symbolic coverage",
    feedsInto: "Human Analyst Interface",
  },
  {
    id: "response",
    name: "Response Orchestrator",
    icon: <Zap className="w-6 h-6" />,
    function: "Coordinates recommended actions",
    whyExists: "Standardizes response workflows",
    limitation: "Cannot execute without human approval",
    feedsInto: "Action Execution Layer",
  },
];

export default function Architecture() {
  return (
    <div className="min-h-screen p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-display text-foreground mb-2">System Architecture</h1>
        <p className="text-muted-foreground">
          Interactive visualization of the neuro-symbolic processing pipeline
        </p>
      </motion.div>

      {/* Interactive Architecture Map */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-12"
      >
        <ArchitectureFlow />
      </motion.div>

      {/* Layer Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-heading text-foreground mb-6">Layer Details</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {layers.map((layer, i) => (
            <motion.div
              key={layer.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.1 }}
              className="card-surface p-6 hover:border-primary/20 transition-colors"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-lg bg-primary/10 text-primary">
                  {layer.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground mb-3">
                    {layer.name}
                  </h3>
                  
                  <div className="space-y-3 text-sm">
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                        Function
                      </p>
                      <p className="text-foreground">{layer.function}</p>
                    </div>
                    
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                        Why It Exists
                      </p>
                      <p className="text-foreground">{layer.whyExists}</p>
                    </div>
                    
                    <div className="p-3 rounded-lg bg-caution/5 border border-caution/20">
                      <div className="flex items-center gap-2 mb-1">
                        <AlertCircle className="w-4 h-4 text-caution" />
                        <p className="text-xs text-caution uppercase tracking-wider">
                          Limitation
                        </p>
                      </div>
                      <p className="text-foreground text-sm">{layer.limitation}</p>
                    </div>
                    
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <span className="text-xs">Feeds into:</span>
                      <span className="text-xs text-primary">{layer.feedsInto}</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
