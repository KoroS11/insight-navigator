import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: "active" | "pending" | "inactive" | "caution" | "info";
  label: string;
  showDot?: boolean;
}

const statusStyles = {
  active: {
    bg: "bg-success/10",
    text: "text-success",
    dot: "bg-success",
  },
  pending: {
    bg: "bg-caution/10",
    text: "text-caution",
    dot: "bg-caution",
  },
  inactive: {
    bg: "bg-muted",
    text: "text-muted-foreground",
    dot: "bg-muted-foreground",
  },
  caution: {
    bg: "bg-caution/10",
    text: "text-caution",
    dot: "bg-caution",
  },
  info: {
    bg: "bg-info/10",
    text: "text-info",
    dot: "bg-info",
  },
};

export function StatusBadge({ status, label, showDot = true }: StatusBadgeProps) {
  const styles = statusStyles[status];

  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-normal rounded",
      styles.bg,
      styles.text
    )}>
      {showDot && <span className={cn("w-1.5 h-1.5 rounded-full", styles.dot)} />}
      {label}
    </span>
  );
}
