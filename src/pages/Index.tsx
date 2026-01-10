import { MetricCard } from "@/components/shared/MetricCard";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { ArchitectureFlow } from "@/components/architecture/ArchitectureFlow";
import { Activity, Database, Brain, Users, Shield, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const trustIndicators = [
  "Built on Zero-Trust Principles",
  "Human Authority Preserved",
  "Full Audit Trail",
  "Explainable by Design",
];

export default function Index() {
  return (
    <div className="min-h-screen p-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-12"
      >
        <div className="flex items-center gap-3 mb-2">
          <StatusBadge status="active" label="System Active" pulse />
          <span className="text-xs text-muted-foreground">Conceptual Demo</span>
        </div>
        <h1 className="text-display text-foreground mb-3">
          Neuro-Symbolic AI for Security Operations
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl">
          Combining neural pattern recognition with symbolic reasoning 
          to deliver explainable, human-auditable security intelligence.
        </p>
      </motion.div>

      {/* Architecture Visualization */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="mb-8"
      >
        <ArchitectureFlow />
      </motion.div>

      {/* Metrics Dashboard */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-heading text-foreground">System Metrics</h2>
          <span className="text-xs text-muted-foreground italic">
            (Illustrative data)
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Events Processed"
            value="1,247"
            icon={<Database className="w-5 h-5" />}
            description="Demo data volume"
          />
          <MetricCard
            label="Explanation Coverage"
            value="100%"
            icon={<Brain className="w-5 h-5" />}
            description="By design"
          />
          <MetricCard
            label="Human Decisions"
            value="89"
            icon={<Users className="w-5 h-5" />}
            description="In this scenario"
          />
          <MetricCard
            label="Reasoning Depth"
            value="4.2"
            icon={<Zap className="w-5 h-5" />}
            description="Average layers"
          />
        </div>
      </motion.div>

      {/* Trust Indicators */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="mb-8"
      >
        <h2 className="text-heading text-foreground mb-4">Trust Principles</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {trustIndicators.map((indicator, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + i * 0.05 }}
              className="card-surface p-4 flex items-center gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Shield className="w-4 h-4 text-primary" />
              </div>
              <span className="text-sm text-foreground">{indicator}</span>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="flex flex-wrap gap-3"
      >
        <Link to="/architecture">
          <Button variant="outline" className="gap-2">
            <Activity className="w-4 h-4" />
            Explore Architecture
          </Button>
        </Link>
        <Link to="/explainability">
          <Button variant="glow" className="gap-2">
            <Brain className="w-4 h-4" />
            View Explainability Demo
          </Button>
        </Link>
      </motion.div>
    </div>
  );
}
