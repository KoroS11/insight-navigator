import { EventSummary } from "@/components/explainability/EventSummary";
import { ExplanationTree } from "@/components/explainability/ExplanationTree";
import { CounterfactualPanel } from "@/components/explainability/CounterfactualPanel";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";

const eventTimeline = [
  { time: "14:32:18.442", event: "NetFlow anomaly detected", type: "system" },
  { time: "14:32:19.103", event: "DNS query correlation completed", type: "system" },
  { time: "14:32:19.887", event: "User behavior analysis completed", type: "system" },
  { time: "14:32:21.234", event: "Policy evaluation completed (2 violations)", type: "system" },
  { time: "14:32:23.009", event: "Explanation generated (depth: 4)", type: "system" },
];

export default function Explainability() {
  return (
    <div className="p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-4">
        <Link to="/" className="hover:text-foreground">Overview</Link>
        <ChevronRight className="w-3 h-3" />
        <span className="text-foreground">Event Analysis</span>
        <ChevronRight className="w-3 h-3" />
        <span className="font-mono">EVT-2026-01-10-0847-LM</span>
      </div>

      <div className="mb-6">
        <h1 className="mb-1">Event Analysis</h1>
        <p className="text-muted-foreground text-sm">
          Detection reasoning and evidence correlation
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-3 gap-6 mb-6">
        {/* Left: Event Summary */}
        <div>
          <EventSummary />
        </div>

        {/* Center: Explanation Tree */}
        <div>
          <ExplanationTree />
        </div>

        {/* Right: Counterfactuals */}
        <div>
          <CounterfactualPanel />
        </div>
      </div>

      {/* Event Timeline */}
      <div className="card-surface">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold">Event Chronicle</h2>
          <span className="text-xs text-muted-foreground">
            Total processing time: 4.567s
          </span>
        </div>
        <div className="p-4">
          <div className="space-y-2">
            {eventTimeline.map((item, i) => (
              <div key={i} className="flex items-center gap-4 text-xs">
                <span className="font-mono text-muted-foreground w-24">{item.time}</span>
                <div className="w-1.5 h-1.5 rounded-full bg-info" />
                <span className="text-foreground">{item.event}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Evidence Strength */}
      <div className="card-surface mt-6">
        <div className="p-4 border-b border-border">
          <h2 className="text-sm font-semibold">Evidence Strength</h2>
        </div>
        <div className="p-4 grid grid-cols-3 gap-6">
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-muted-foreground">Network Behavior</span>
              <span className="font-mono">82/100</span>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-info rounded-full" style={{ width: "82%" }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-muted-foreground">User Context</span>
              <span className="font-mono">45/100</span>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-caution rounded-full" style={{ width: "45%" }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-muted-foreground">Historical Match</span>
              <span className="font-mono">77/100</span>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-info rounded-full" style={{ width: "77%" }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
