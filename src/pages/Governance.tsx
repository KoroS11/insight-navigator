import { motion } from "framer-motion";
import { AutonomyBoundary } from "@/components/governance/AutonomyBoundary";
import { AuditTrail } from "@/components/governance/AuditTrail";
import { Shield, Key, Lock, Clock } from "lucide-react";

export default function Governance() {
  return (
    <div className="min-h-screen p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-primary/10">
            <Shield className="w-5 h-5 text-primary" />
          </div>
          <h1 className="text-display text-foreground">Governance & Policy</h1>
        </div>
        <p className="text-muted-foreground">
          Autonomy boundaries, audit trails, and override protocols
        </p>
      </motion.div>

      {/* Autonomy Boundaries */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-8"
      >
        <h2 className="text-heading text-foreground mb-4">Autonomy Boundaries</h2>
        <AutonomyBoundary />
      </motion.div>

      {/* Override Protocol */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-8"
      >
        <h2 className="text-heading text-foreground mb-4">Emergency Override Protocol</h2>
        <div className="card-surface p-6">
          <p className="text-sm text-muted-foreground mb-6">
            Conceptual framework for emergency human override of system recommendations
          </p>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 mb-2">
                <Key className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-foreground">Requires</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Multi-factor authentication
              </p>
            </div>
            
            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 mb-2">
                <Lock className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-foreground">Logged to</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Immutable audit trail
              </p>
            </div>
            
            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-foreground">Notifies</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Security leadership
              </p>
            </div>
            
            <div className="p-4 rounded-lg bg-muted/50">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-foreground">Expires</span>
              </div>
              <p className="text-xs text-muted-foreground">
                After 4 hours or manual revocation
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Audit Trail */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-heading text-foreground mb-4">Audit Trail Viewer</h2>
        <AuditTrail />
      </motion.div>
    </div>
  );
}
