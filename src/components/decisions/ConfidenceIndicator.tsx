import { motion } from "framer-motion";

interface ConfidenceIndicatorProps {
  level: "low" | "moderate" | "high";
  reasoning: string;
}

export function ConfidenceIndicator({ level, reasoning }: ConfidenceIndicatorProps) {
  const levelValues = {
    low: 25,
    moderate: 55,
    high: 85,
  };

  const levelColors = {
    low: "bg-destructive",
    moderate: "bg-caution",
    high: "bg-success",
  };

  return (
    <div className="card-surface p-5">
      <div className="text-center mb-4">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">
          System Confidence
        </h3>
        <p className="text-xl font-semibold text-foreground uppercase">
          {level}
        </p>
      </div>

      <div className="relative h-3 bg-muted rounded-full overflow-hidden mb-4">
        <motion.div
          className={`absolute inset-y-0 left-0 ${levelColors[level]} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${levelValues[level]}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
        <div className="absolute inset-0 flex justify-between px-1 items-center">
          <span className="text-[10px] text-muted-foreground">Low</span>
          <span className="text-[10px] text-muted-foreground">High</span>
        </div>
      </div>

      <p className="text-xs text-muted-foreground text-center">
        {reasoning}
      </p>
    </div>
  );
}
