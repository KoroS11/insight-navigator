import { cn } from "@/lib/utils";

interface ConfidenceIndicatorProps {
  score: number;
  breakdown: {
    label: string;
    score: number;
    isWarning?: boolean;
  }[];
  responseTime: string;
}

export function ConfidenceIndicator({ score, breakdown, responseTime }: ConfidenceIndicatorProps) {
  const getScoreLevel = (s: number) => {
    if (s >= 70) return { label: "HIGH", color: "text-caution" };
    if (s >= 40) return { label: "MODERATE", color: "text-info" };
    return { label: "LOW", color: "text-muted-foreground" };
  };

  const level = getScoreLevel(score);

  return (
    <div className="card-surface p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold">Threat Likelihood</h3>
        <span className={cn("text-xs font-semibold", level.color)}>
          {level.label}
        </span>
      </div>

      {/* Main Score */}
      <div className="mb-4">
        <div className="flex items-baseline gap-1 mb-2">
          <span className="text-3xl font-semibold">{score}</span>
          <span className="text-muted-foreground text-sm">/100</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div 
            className={cn(
              "h-full rounded-full transition-all",
              score >= 70 ? "bg-caution" : score >= 40 ? "bg-info" : "bg-muted-foreground"
            )}
            style={{ width: `${score}%` }}
          />
        </div>
      </div>

      {/* Breakdown */}
      <div className="space-y-2 pt-3 border-t border-border">
        {breakdown.map((item, i) => (
          <div key={i} className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">{item.label}</span>
            <span className={cn(
              "font-mono",
              item.isWarning ? "text-caution" : "text-foreground"
            )}>
              {item.score}/100 {item.isWarning && "⚠"}
            </span>
          </div>
        ))}
      </div>

      {/* Response Time */}
      <div className="mt-4 pt-3 border-t border-border">
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Recommended response</span>
          <span className="text-caution font-medium">{responseTime}</span>
        </div>
      </div>
    </div>
  );
}
