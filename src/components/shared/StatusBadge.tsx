import { cn } from "@/lib/utils";

type StatusType = "active" | "pending" | "inactive" | "caution" | "info";

interface StatusBadgeProps {
  status: StatusType;
  label: string;
  pulse?: boolean;
  className?: string;
}

const statusStyles: Record<StatusType, string> = {
  active: "bg-success/10 text-success border-success/20",
  pending: "bg-caution/10 text-caution border-caution/20",
  inactive: "bg-muted text-muted-foreground border-border",
  caution: "bg-caution/10 text-caution border-caution/20",
  info: "bg-info/10 text-info border-info/20",
};

export function StatusBadge({ status, label, pulse, className }: StatusBadgeProps) {
  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border",
      statusStyles[status],
      className
    )}>
      {pulse && (
        <span className={cn(
          "w-1.5 h-1.5 rounded-full",
          status === "active" && "bg-success animate-pulse-subtle",
          status === "pending" && "bg-caution animate-pulse-subtle",
          status === "caution" && "bg-caution animate-pulse-subtle",
          status === "info" && "bg-info",
          status === "inactive" && "bg-muted-foreground"
        )} />
      )}
      {label}
    </span>
  );
}
