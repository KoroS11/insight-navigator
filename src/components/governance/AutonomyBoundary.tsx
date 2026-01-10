import { cn } from "@/lib/utils";

interface ControlRow {
  action: string;
  autonomy: "Full" | "Limited" | "None" | "Never";
  approval: string;
}

const controlMatrix: ControlRow[] = [
  { action: "Detect anomalies", autonomy: "Full", approval: "None" },
  { action: "Analyze patterns", autonomy: "Full", approval: "None" },
  { action: "Generate recommendations", autonomy: "Full", approval: "None" },
  { action: "Send alerts", autonomy: "Full", approval: "None" },
  { action: "Log all actions", autonomy: "Full", approval: "None" },
  { action: "Block traffic (temp)", autonomy: "None", approval: "Analyst" },
  { action: "Isolate system", autonomy: "None", approval: "Analyst" },
  { action: "Kill process", autonomy: "None", approval: "Lead Analyst" },
  { action: "Modify firewall rules", autonomy: "None", approval: "Admin" },
  { action: "Delete/quarantine files", autonomy: "Never", approval: "Admin + CISO" },
];

const autonomyStyles = {
  Full: "text-success",
  Limited: "text-caution",
  None: "text-muted-foreground",
  Never: "text-destructive",
};

export function AutonomyBoundary() {
  return (
    <div className="card-surface">
      <div className="p-4 border-b border-border">
        <h3 className="text-sm font-semibold">Control Matrix</h3>
        <p className="text-xs text-muted-foreground mt-1">
          System autonomy boundaries and approval requirements
        </p>
      </div>
      
      <table className="data-table">
        <thead>
          <tr>
            <th>Action</th>
            <th className="w-24 text-center">Autonomy</th>
            <th className="w-32">Approval Required</th>
          </tr>
        </thead>
        <tbody>
          {controlMatrix.map((row, i) => (
            <tr key={i}>
              <td>{row.action}</td>
              <td className={cn("text-center font-medium text-xs", autonomyStyles[row.autonomy])}>
                {row.autonomy}
              </td>
              <td className="text-xs text-muted-foreground">{row.approval}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
