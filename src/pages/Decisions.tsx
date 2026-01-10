import { ConfidenceIndicator } from "@/components/decisions/ConfidenceIndicator";
import { ActionMatrix } from "@/components/decisions/ActionMatrix";
import { AnalystNotes } from "@/components/decisions/AnalystNotes";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";

const confidenceData = {
  score: 68,
  breakdown: [
    { label: "Behavior score", score: 82, isWarning: true },
    { label: "Context score", score: 45 },
    { label: "Historical match", score: 77 },
  ],
  responseTime: "< 15 minutes",
};

export default function Decisions() {
  return (
    <div className="p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-4">
        <Link to="/" className="hover:text-foreground">Overview</Link>
        <ChevronRight className="w-3 h-3" />
        <Link to="/explainability" className="hover:text-foreground">Event Analysis</Link>
        <ChevronRight className="w-3 h-3" />
        <span className="text-foreground">Decision</span>
      </div>

      <div className="mb-6">
        <h1 className="mb-1">Analyst Decision</h1>
        <p className="text-muted-foreground text-sm">
          Review threat assessment and record decision
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <ConfidenceIndicator {...confidenceData} />
          <ActionMatrix recommendedAction="escalate" />
        </div>

        {/* Right Column */}
        <div>
          <AnalystNotes />
        </div>
      </div>

      {/* Playbook Reference */}
      <div className="card-surface mt-6">
        <div className="p-4 border-b border-border">
          <h2 className="text-sm font-semibold">Relevant Playbooks</h2>
        </div>
        <div className="p-4">
          <table className="data-table">
            <thead>
              <tr>
                <th>Playbook</th>
                <th>Trigger Condition</th>
                <th>Est. Duration</th>
                <th>Last Updated</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="text-primary">PB-LM-001: Lateral Movement Response</td>
                <td className="text-xs text-muted-foreground">Lateral movement + privilege escalation</td>
                <td className="font-mono text-xs">2-4 hours</td>
                <td className="font-mono text-xs text-muted-foreground">2025-12-15</td>
              </tr>
              <tr>
                <td className="text-primary">PB-DE-003: Data Exfiltration Triage</td>
                <td className="text-xs text-muted-foreground">Outbound anomaly to external IP</td>
                <td className="font-mono text-xs">1-2 hours</td>
                <td className="font-mono text-xs text-muted-foreground">2025-11-28</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
