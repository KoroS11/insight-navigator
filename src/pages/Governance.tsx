import { AutonomyBoundary } from "@/components/governance/AutonomyBoundary";
import { AuditTrail } from "@/components/governance/AuditTrail";
import { Lock, Key, Bell, Clock } from "lucide-react";

export default function Governance() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="mb-1">Governance & Policy</h1>
        <p className="text-muted-foreground text-sm">
          Autonomy boundaries, audit trails, and override protocols
        </p>
      </div>

      {/* Control Matrix */}
      <div className="mb-6">
        <AutonomyBoundary />
      </div>

      {/* Emergency Override */}
      <div className="card-surface mb-6">
        <div className="p-4 border-b border-border">
          <h2 className="text-sm font-semibold">Emergency Override Protocol</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Procedures for human override of system boundaries in critical situations
          </p>
        </div>
        <div className="p-4 grid grid-cols-4 gap-4">
          <div className="p-3 bg-accent/30 rounded">
            <div className="flex items-center gap-2 mb-2">
              <Key className="w-4 h-4 text-primary" />
              <span className="text-xs font-semibold">Authentication</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Multi-factor required. Hardware token + biometric for blocking actions.
            </p>
          </div>
          <div className="p-3 bg-accent/30 rounded">
            <div className="flex items-center gap-2 mb-2">
              <Lock className="w-4 h-4 text-primary" />
              <span className="text-xs font-semibold">Audit</span>
            </div>
            <p className="text-xs text-muted-foreground">
              All overrides logged to immutable audit trail with full context capture.
            </p>
          </div>
          <div className="p-3 bg-accent/30 rounded">
            <div className="flex items-center gap-2 mb-2">
              <Bell className="w-4 h-4 text-primary" />
              <span className="text-xs font-semibold">Notification</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Security leadership notified within 60 seconds of any override action.
            </p>
          </div>
          <div className="p-3 bg-accent/30 rounded">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-primary" />
              <span className="text-xs font-semibold">Expiration</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Override permissions auto-expire after 4 hours or manual revocation.
            </p>
          </div>
        </div>
      </div>

      {/* Audit Trail */}
      <AuditTrail />
    </div>
  );
}
