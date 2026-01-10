import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: "up" | "down" | "neutral";
  description?: string;
  className?: string;
}

export function MetricCard({ 
  label, 
  value, 
  icon, 
  description,
  className 
}: MetricCardProps) {
  return (
    <div className={cn(
      "card-surface p-6 transition-all duration-200 hover:border-primary/20",
      className
    )}>
      <div className="flex items-start justify-between mb-3">
        <span className="metric-label">{label}</span>
        {icon && (
          <div className="text-muted-foreground">
            {icon}
          </div>
        )}
      </div>
      <div className="metric-value mb-1">{value}</div>
      {description && (
        <p className="text-caption text-muted-foreground">{description}</p>
      )}
    </div>
  );
}
