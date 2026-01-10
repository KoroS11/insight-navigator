import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  trend?: {
    direction: "up" | "down" | "flat";
    value: string;
    label?: string;
  };
  className?: string;
}

export function MetricCard({ label, value, subValue, trend, className }: MetricCardProps) {
  const trendIcon = {
    up: <TrendingUp className="w-3 h-3" />,
    down: <TrendingDown className="w-3 h-3" />,
    flat: <Minus className="w-3 h-3" />,
  };

  const trendColor = {
    up: "text-success",
    down: "text-destructive",
    flat: "text-muted-foreground",
  };

  return (
    <div className={cn("card-surface p-4", className)}>
      <p className="metric-label mb-1">{label}</p>
      <div className="flex items-baseline gap-2">
        <span className="metric-value">{value}</span>
        {subValue && (
          <span className="text-xs text-muted-foreground">{subValue}</span>
        )}
      </div>
      {trend && (
        <div className={cn("flex items-center gap-1 mt-2 text-xs", trendColor[trend.direction])}>
          {trendIcon[trend.direction]}
          <span>{trend.value}</span>
          {trend.label && (
            <span className="text-muted-foreground ml-1">{trend.label}</span>
          )}
        </div>
      )}
    </div>
  );
}
