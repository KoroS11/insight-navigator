"""
NSA-X Layer 6: Explainability Engine Service
Generates human-readable explanations and counterfactuals.
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Alert,
    Event,
    Explanation,
    NeuralDetection,
    ProcessedEvent,
    RuleEvaluation,
)


class ExplainabilityService:
    """Layer 6: Generates explanations for alerts and detections."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_explanation(
        self,
        alert: Alert,
        detection: NeuralDetection,
        evaluations: list[RuleEvaluation],
        processed_event: ProcessedEvent,
        event: Event,
    ) -> Explanation:
        """
        Generate human-readable explanation for an alert.
        
        Critical Rules:
        - Must explain BOTH neural and symbolic reasoning
        - Must include counterfactual suggestions
        - Language must be analyst-friendly (not ML jargon)
        - Must be deterministic
        - Must complete in <100ms
        """
        # Build the explanation tree
        explanation_tree = self._build_explanation_tree(
            alert=alert,
            detection=detection,
            evaluations=evaluations,
        )
        
        # Generate natural language summary
        natural_language = self._generate_natural_language(
            alert=alert,
            detection=detection,
            evaluations=evaluations,
            event=event,
        )
        
        # Generate counterfactuals
        counterfactuals = self._generate_counterfactuals(
            detection=detection,
            evaluations=evaluations,
            processed_event=processed_event,
        )
        
        explanation = Explanation(
            id=uuid.uuid4(),
            alert_id=alert.id,
            explanation_data={
                "tree": explanation_tree,
                "natural_language": natural_language,
                "counterfactuals": counterfactuals,
            },
            generated_at=datetime.now(timezone.utc),
        )
        
        self.db.add(explanation)
        await self.db.flush()
        
        return explanation
    
    def _build_explanation_tree(
        self,
        alert: Alert,
        detection: NeuralDetection,
        evaluations: list[RuleEvaluation],
    ) -> dict[str, Any]:
        """
        Build a structured explanation tree.
        Format suitable for UI visualization.
        """
        tree = {
            "root": {
                "type": "alert",
                "classification": alert.classification,
                "composite_risk_score": alert.composite_risk_score,
                "children": [],
            }
        }
        
        # Neural detection branch
        neural_branch = {
            "type": "neural_detection",
            "anomaly_score": detection.anomaly_score,
            "children": [
                {
                    "type": "factor",
                    "name": "frequency_analysis",
                    "score": detection.frequency_score,
                    "description": self._describe_frequency_score(detection.frequency_score),
                },
                {
                    "type": "factor",
                    "name": "port_analysis",
                    "score": detection.port_score,
                    "description": self._describe_port_score(detection.port_score),
                },
                {
                    "type": "factor",
                    "name": "temporal_analysis",
                    "score": detection.temporal_score,
                    "description": self._describe_temporal_score(detection.temporal_score),
                },
                {
                    "type": "factor",
                    "name": "geographic_analysis",
                    "score": detection.geographic_score,
                    "description": self._describe_geographic_score(detection.geographic_score),
                },
            ],
        }
        tree["root"]["children"].append(neural_branch)
        
        # Symbolic reasoning branch
        matched_rules = [e for e in evaluations if e.matched]
        if matched_rules:
            symbolic_branch = {
                "type": "symbolic_reasoning",
                "rules_matched": len(matched_rules),
                "children": [
                    {
                        "type": "rule_match",
                        "rule_id": e.rule_id,
                        "severity": e.severity,
                    }
                    for e in matched_rules
                ],
            }
            tree["root"]["children"].append(symbolic_branch)
        
        return tree
    
    def _generate_natural_language(
        self,
        alert: Alert,
        detection: NeuralDetection,
        evaluations: list[RuleEvaluation],
        event: Event,
    ) -> str:
        """Generate analyst-friendly explanation text."""
        parts = []
        
        # Opening statement
        parts.append(
            f"This {alert.classification} classification alert (risk score: {alert.composite_risk_score}/100) "
            f"was triggered by activity from {event.source_ip}."
        )
        
        # Neural detection explanation
        score_desc = "low" if detection.anomaly_score < 0.4 else \
                     "moderate" if detection.anomaly_score < 0.7 else "high"
        parts.append(
            f"\n\nAnomaly Detection: The system detected {score_desc} anomaly "
            f"(score: {detection.anomaly_score:.2f}/1.0)."
        )
        
        # Explain contributing factors
        factors = []
        if detection.frequency_score >= 0.5:
            factors.append(f"unusual event frequency ({detection.frequency_score:.2f})")
        if detection.port_score >= 0.5:
            factors.append(f"suspicious port usage ({detection.port_score:.2f})")
        if detection.temporal_score >= 0.5:
            factors.append(f"off-hours timing ({detection.temporal_score:.2f})")
        if detection.geographic_score >= 0.5:
            factors.append(f"unusual network location ({detection.geographic_score:.2f})")
        
        if factors:
            parts.append(f" Contributing factors: {', '.join(factors)}.")
        
        # Rule matches
        matched = [e for e in evaluations if e.matched]
        if matched:
            parts.append("\n\nPolicy Violations:")
            for m in matched:
                rule_desc = self._get_rule_description(m.rule_id)
                parts.append(f"\n• {m.rule_id}: {rule_desc} (Severity: {m.severity})")
        
        return "".join(parts)
    
    def _generate_counterfactuals(
        self,
        detection: NeuralDetection,
        evaluations: list[RuleEvaluation],
        processed_event: ProcessedEvent,
    ) -> list[dict[str, Any]]:
        """
        Generate counterfactual suggestions.
        "The alert would NOT have triggered if..."
        """
        counterfactuals = []
        
        # Temporal counterfactual
        temporal = processed_event.parsed_fields.get("temporal", {})
        if not temporal.get("is_business_hours", True):
            counterfactuals.append({
                "type": "temporal",
                "condition": "Activity occurred during business hours (9 AM - 5 PM)",
                "impact": "Off-hours rule would not have matched",
                "factor_affected": "temporal_score",
                "potential_reduction": 0.3,
            })
        
        # Frequency counterfactual
        if detection.frequency_score >= 0.5:
            counterfactuals.append({
                "type": "frequency",
                "condition": "Fewer than 50 events from this source in 24 hours",
                "impact": "Frequency anomaly would not have been flagged",
                "factor_affected": "frequency_score",
                "potential_reduction": 0.4,
            })
        
        # Port counterfactual
        if detection.port_score >= 0.5:
            network = processed_event.parsed_fields.get("network", {})
            dest_port = network.get("destination", {}).get("port")
            if dest_port and dest_port > 1023:
                counterfactuals.append({
                    "type": "port",
                    "condition": f"Connection used a well-known port instead of {dest_port}",
                    "impact": "Port anomaly score would be lower",
                    "factor_affected": "port_score",
                    "potential_reduction": 0.3,
                })
        
        # Geographic counterfactual
        if detection.geographic_score >= 0.5:
            counterfactuals.append({
                "type": "geographic",
                "condition": "Source was from an internal IP range",
                "impact": "Network boundary rules would not have matched",
                "factor_affected": "geographic_score",
                "potential_reduction": 0.4,
            })
        
        # Add overall impact assessment
        for cf in counterfactuals:
            reduction = cf["potential_reduction"]
            new_score = detection.anomaly_score - (reduction * 0.25)
            cf["projected_anomaly_score"] = max(0.0, round(new_score, 2))
            cf["would_prevent_alert"] = new_score < 0.7
        
        return counterfactuals
    
    def _describe_frequency_score(self, score: float) -> str:
        """Human-readable frequency score description."""
        if score < 0.3:
            return "Normal event frequency from this source"
        elif score < 0.6:
            return "Slightly elevated event frequency"
        elif score < 0.8:
            return "High event frequency, potential scanning activity"
        else:
            return "Very high frequency, possible automated attack"
    
    def _describe_port_score(self, score: float) -> str:
        """Human-readable port score description."""
        if score < 0.3:
            return "Common, well-known destination port"
        elif score < 0.6:
            return "Registered port, typically application traffic"
        elif score < 0.8:
            return "High port number, often used by custom applications"
        else:
            return "Unusual port, commonly associated with suspicious activity"
    
    def _describe_temporal_score(self, score: float) -> str:
        """Human-readable temporal score description."""
        if score < 0.3:
            return "Activity during normal business hours"
        elif score < 0.6:
            return "Activity outside typical patterns"
        else:
            return "Activity during unusual hours (nights/weekends)"
    
    def _describe_geographic_score(self, score: float) -> str:
        """Human-readable geographic score description."""
        if score < 0.3:
            return "Internal network communication"
        elif score < 0.6:
            return "Standard external communication pattern"
        else:
            return "Communication with unusual network segment"
    
    def _get_rule_description(self, rule_id: str) -> str:
        """Get human-readable rule description."""
        descriptions = {
            "RULE-001": "Off-hours service account usage detected",
            "RULE-002": "High-frequency events from single source",
            "RULE-003": "Unusual port access pattern",
            "RULE-004": "Access to high criticality asset",
            "RULE-005": "External source connecting to internal system",
        }
        return descriptions.get(rule_id, f"Rule {rule_id} violation")
    
    async def get_explanation(self, alert_id: uuid.UUID) -> Explanation | None:
        """Get explanation for an alert."""
        result = await self.db.execute(
            select(Explanation).where(Explanation.alert_id == alert_id)
        )
        return result.scalar_one_or_none()
