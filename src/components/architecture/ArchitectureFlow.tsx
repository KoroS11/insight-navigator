import { motion } from "framer-motion";

const layers = [
  { id: "input", label: "Data Input", x: 80, y: 60, description: "Network telemetry, logs, events" },
  { id: "neural", label: "Neural Detection", x: 280, y: 60, description: "Pattern recognition layer" },
  { id: "symbolic", label: "Symbolic Reasoning", x: 480, y: 60, description: "Rule-based analysis" },
  { id: "explain", label: "Explanation Engine", x: 380, y: 180, description: "Human-readable output" },
  { id: "human", label: "Human Analyst", x: 380, y: 300, description: "Final authority" },
];

const connections = [
  { from: "input", to: "neural" },
  { from: "neural", to: "symbolic" },
  { from: "neural", to: "explain" },
  { from: "symbolic", to: "explain" },
  { from: "explain", to: "human" },
];

export function ArchitectureFlow() {
  const getLayerPos = (id: string) => {
    const layer = layers.find(l => l.id === id);
    return layer ? { x: layer.x, y: layer.y } : { x: 0, y: 0 };
  };

  return (
    <div className="relative w-full h-[400px] card-surface rounded-xl overflow-hidden">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 600 400">
        {/* Grid Pattern */}
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="hsl(210 20% 16%)" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Connections */}
        {connections.map((conn, i) => {
          const from = getLayerPos(conn.from);
          const to = getLayerPos(conn.to);
          return (
            <motion.line
              key={i}
              x1={from.x + 60}
              y1={from.y + 25}
              x2={to.x + 60}
              y2={to.y + 25}
              stroke="hsl(200 80% 55%)"
              strokeWidth="2"
              strokeOpacity="0.3"
              className="flow-line"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1, delay: i * 0.2 }}
            />
          );
        })}

        {/* Nodes */}
        {layers.map((layer, i) => (
          <motion.g
            key={layer.id}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
          >
            <rect
              x={layer.x}
              y={layer.y}
              width="120"
              height="50"
              rx="8"
              fill="hsl(210 25% 10%)"
              stroke="hsl(200 80% 55%)"
              strokeWidth="1"
              strokeOpacity="0.5"
            />
            <text
              x={layer.x + 60}
              y={layer.y + 22}
              textAnchor="middle"
              fill="hsl(210 20% 90%)"
              fontSize="11"
              fontWeight="500"
            >
              {layer.label}
            </text>
            <text
              x={layer.x + 60}
              y={layer.y + 38}
              textAnchor="middle"
              fill="hsl(210 15% 50%)"
              fontSize="8"
            >
              {layer.description.slice(0, 20)}...
            </text>
          </motion.g>
        ))}

        {/* Active Indicator */}
        <motion.circle
          cx="340"
          cy="85"
          r="4"
          fill="hsl(200 80% 55%)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </svg>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 flex items-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5 bg-primary/50" />
          <span>Data Flow</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse-subtle" />
          <span>Active Processing</span>
        </div>
      </div>
    </div>
  );
}
