const layers = [
  { id: "input", label: "Data Ingestion", x: 60, y: 50, 
    stats: "Syslog, SNMP, CEF | ~4.2K events/min" },
  { id: "neural", label: "Anomaly Detection", x: 240, y: 50, 
    stats: "512-dim embeddings | <200ms" },
  { id: "symbolic", label: "Rule Engine", x: 420, y: 50, 
    stats: "847 active rules | <50ms" },
  { id: "explain", label: "Explanation", x: 330, y: 150, 
    stats: "4.2 avg depth | <100ms" },
  { id: "human", label: "Analyst Queue", x: 330, y: 250, 
    stats: "3 pending | 2 active" },
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
    <div className="relative w-full h-[320px] card-surface overflow-hidden">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 540 320">
        {/* Subtle Grid */}
        <defs>
          <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="hsl(220 14% 12%)" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Connections */}
        {connections.map((conn, i) => {
          const from = getLayerPos(conn.from);
          const to = getLayerPos(conn.to);
          return (
            <line
              key={i}
              x1={from.x + 60}
              y1={from.y + 22}
              x2={to.x + 60}
              y2={to.y + 22}
              stroke="hsl(199 70% 50%)"
              strokeWidth="1"
              strokeOpacity="0.3"
              className="flow-line"
            />
          );
        })}

        {/* Nodes */}
        {layers.map((layer) => (
          <g key={layer.id}>
            <rect
              x={layer.x}
              y={layer.y}
              width="120"
              height="44"
              rx="2"
              fill="hsl(220 16% 11%)"
              stroke="hsl(220 14% 18%)"
              strokeWidth="1"
            />
            <text
              x={layer.x + 60}
              y={layer.y + 18}
              textAnchor="middle"
              fill="hsl(220 10% 88%)"
              fontSize="11"
              fontWeight="600"
            >
              {layer.label}
            </text>
            <text
              x={layer.x + 60}
              y={layer.y + 32}
              textAnchor="middle"
              fill="hsl(220 10% 50%)"
              fontSize="8"
              fontFamily="JetBrains Mono, monospace"
            >
              {layer.stats.slice(0, 28)}
            </text>
          </g>
        ))}
      </svg>

      {/* Legend */}
      <div className="absolute bottom-3 left-4 flex items-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-px bg-primary/50" />
          <span>Data flow</span>
        </div>
      </div>
    </div>
  );
}
