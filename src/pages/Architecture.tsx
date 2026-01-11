import { ArchitectureFlow } from "@/components/architecture/ArchitectureFlow";

interface LayerDetail {
  id: string;
  name: string;
  implementation: string;
  latency: string;
  throughput: string;
  limitation: string;
}

const layers: LayerDetail[] = [
  {
    id: "neural",
    name: "Anomaly Detection",
    implementation: "Transformer-based (512-dim embeddings), trained on 18M labeled events",
    latency: "< 200ms",
    throughput: "~4.2K events/min",
    limitation: "Cannot explain its own decisions; requires symbolic layer for interpretability",
  },
  {
    id: "symbolic",
    name: "Rule Engine",
    implementation: "Prolog-style inference with 847 active rules, supports temporal reasoning",
    latency: "< 50ms",
    throughput: "~12K evaluations/min",
    limitation: "Requires neural layer for novel pattern detection",
  },
  {
    id: "explain",
    name: "Explanation Engine",
    implementation: "Causal chain reconstruction with counterfactual generation",
    latency: "< 100ms",
    throughput: "~6K explanations/min",
    limitation: "Explanation depth limited by symbolic rule coverage",
  },
  {
    id: "response",
    name: "Response Orchestrator",
    implementation: "Workflow engine with playbook integration, SOAR compatible",
    latency: "< 20ms",
    throughput: "~8K recommendations/min",
    limitation: "Cannot execute without human approval for blocking actions",
  },
];

export default function Architecture() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="mb-1">System Architecture</h1>
        <p className="text-muted-foreground text-sm">
          Neuro-symbolic processing pipeline with real-time telemetry
        </p>
      </div>

      {/* Architecture Diagram */}
      <div className="mb-8">
        <ArchitectureFlow />
      </div>

      {/* Layer Details Table */}
      <div className="card-surface">
        <div className="p-4 border-b border-border">
          <h2 className="text-sm font-semibold">Layer Specifications</h2>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th className="w-40">Layer</th>
              <th>Implementation</th>
              <th className="w-24">Latency</th>
              <th className="w-32">Throughput</th>
              <th>Limitation</th>
            </tr>
          </thead>
          <tbody>
            {layers.map((layer) => (
              <tr key={layer.id}>
                <td className="font-semibold text-foreground">{layer.name}</td>
                <td className="text-xs text-muted-foreground">{layer.implementation}</td>
                <td className="font-mono text-xs">{layer.latency}</td>
                <td className="font-mono text-xs">{layer.throughput}</td>
                <td className="text-xs text-caution">{layer.limitation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Protocol Support */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="card-surface p-4">
          <h3 className="text-xs font-semibold mb-3">Input Protocols</h3>
          <div className="space-y-1 text-xs text-muted-foreground font-mono">
            <p>Syslog (RFC 5424)</p>
            <p>SNMP v2c/v3</p>
            <p>CEF (Common Event Format)</p>
            <p>LEEF (Log Event Extended Format)</p>
            <p>NetFlow v9 / IPFIX</p>
          </div>
        </div>

        <div className="card-surface p-4">
          <h3 className="text-xs font-semibold mb-3">Detection Capabilities</h3>
          <div className="space-y-1 text-xs text-muted-foreground">
            <p>Lateral movement detection</p>
            <p>Privilege escalation patterns</p>
            <p>Data exfiltration indicators</p>
            <p>C2 beacon identification</p>
            <p>Credential abuse detection</p>
          </div>
        </div>

        <div className="card-surface p-4">
          <h3 className="text-xs font-semibold mb-3">Integration Points</h3>
          <div className="space-y-1 text-xs text-muted-foreground font-mono">
            <p>REST API (OpenAPI 3.0)</p>
            <p>Webhook notifications</p>
            <p>SIEM export (JSON, CEF)</p>
            <p>SOAR playbook triggers</p>
            <p>Slack / Teams alerts</p>
          </div>
        </div>
      </div>
    </div>
  );
}
