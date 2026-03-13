"""
NSA-X Layer 4: Symbolic Reasoning Service
Applies security rules and policies - NO machine learning here.
"""
import ipaddress
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProcessedEvent, Rule, RuleEvaluation

# Default rules for MVP
DEFAULT_RULES = [
    {
        "rule_id": "RULE-001",
        "name": "Off-hours service account usage",
        "category": "temporal_violation",
        "conditions": {
            "temporal.is_business_hours": False,
            "event_type_contains": "auth",
        },
        "severity": "HIGH",
    },
    {
        "rule_id": "RULE-002",
        "name": "High-frequency events from single source",
        "category": "frequency_anomaly",
        "conditions": {
            "frequency_threshold": 50,
        },
        "severity": "MEDIUM",
    },
    {
        "rule_id": "RULE-003",
        "name": "Unusual port access",
        "category": "port_violation",
        "conditions": {
            "dest_port_above": 8000,
        },
        "severity": "HIGH",
    },
    {
        "rule_id": "RULE-004",
        "name": "High criticality asset access",
        "category": "asset_protection",
        "conditions": {
            "asset_criticality_above": 80,
        },
        "severity": "MEDIUM",
    },
    {
        "rule_id": "RULE-005",
        "name": "External to internal connection",
        "category": "network_boundary",
        "conditions": {
            "source_external": True,
            "dest_internal": True,
        },
        "severity": "HIGH",
    },
]


INTERNAL_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


class SymbolicReasoningService:
    """Layer 4: Rule-based security policy evaluation."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def ensure_default_rules(self) -> None:
        """Ensure default rules exist in the database."""
        for rule_data in DEFAULT_RULES:
            existing = await self.db.execute(
                select(Rule).where(Rule.rule_id == rule_data["rule_id"])
            )
            if existing.scalar_one_or_none() is None:
                rule = Rule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    category=rule_data["category"],
                    conditions=rule_data["conditions"],
                    severity=rule_data["severity"],
                    enabled=True,
                    created_at=datetime.now(timezone.utc),
                )
                self.db.add(rule)
        await self.db.flush()
    
    async def evaluate_rules(
        self,
        processed_event: ProcessedEvent,
        event_count_24h: int = 0,
    ) -> list[RuleEvaluation]:
        """
        Evaluate all enabled rules against a processed event.
        
        Critical Rules:
        - NO machine learning here
        - NO anomaly detection (that's Layer 3)
        - Only explicit rule evaluation
        - Rules must be deterministic (same input = same output)
        - Must complete in <150ms per event
        """
        # Get all enabled rules
        result = await self.db.execute(
            select(Rule).where(Rule.enabled == True)
        )
        rules = list(result.scalars().all())
        
        evaluations = []
        parsed = processed_event.parsed_fields
        
        for rule in rules:
            matched = self._evaluate_rule(
                rule=rule,
                parsed_fields=parsed,
                asset_criticality=processed_event.asset_criticality or 50,
                event_count_24h=event_count_24h,
            )
            
            evaluation = RuleEvaluation(
                id=uuid.uuid4(),
                processed_event_id=processed_event.id,
                rule_id=rule.rule_id,
                matched=matched,
                severity=rule.severity if matched else None,
                evaluation_timestamp=datetime.now(timezone.utc),
            )
            self.db.add(evaluation)
            evaluations.append(evaluation)
        
        await self.db.flush()
        return evaluations
    
    def _evaluate_rule(
        self,
        rule: Rule,
        parsed_fields: dict[str, Any],
        asset_criticality: int,
        event_count_24h: int,
    ) -> bool:
        """
        Evaluate a single rule against event data.
        Returns True if rule matches (violation detected).
        """
        conditions = rule.conditions
        
        # Get nested values safely
        temporal = parsed_fields.get("temporal", {})
        network = parsed_fields.get("network", {})
        source = network.get("source", {})
        dest = network.get("destination", {})
        
        # RULE-001: Off-hours activity with auth events
        if rule.rule_id == "RULE-001":
            is_business = temporal.get("is_business_hours", True)
            if is_business:
                return False  # Within business hours - no violation
            
            # Check if event_type contains "auth" as per rule conditions
            event_type_contains = conditions.get("event_type_contains", "")
            event_type = parsed_fields.get("event_type", "")
            if event_type_contains and event_type_contains not in event_type.lower():
                return False  # Not an auth event - no violation
            
            return True  # Off-hours auth event - violation
        
        # RULE-002: High frequency OR malicious port
        if rule.rule_id == "RULE-002":
            # Check for malicious ports first
            if "dest_ports" in conditions:
                malicious_ports = conditions.get("dest_ports", [])
                dest_port = dest.get("port")
                if dest_port is not None and dest_port in malicious_ports:
                    return True
            # Then check frequency
            threshold = conditions.get("frequency_threshold", 50)
            return event_count_24h > threshold
        
        # RULE-003: Unusual port
        if rule.rule_id == "RULE-003":
            port_threshold = conditions.get("dest_port_above", 8000)
            dest_port = dest.get("port")
            if dest_port is not None:
                return dest_port > port_threshold
            return False
        
        # RULE-004: High criticality asset
        if rule.rule_id == "RULE-004":
            threshold = conditions.get("asset_criticality_above", 80)
            return asset_criticality > threshold
        
        # RULE-005: External to internal
        if rule.rule_id == "RULE-005":
            source_ip = source.get("ip", "")
            dest_ip = dest.get("ip", "")

            def _is_internal_ip(ip_value: str) -> bool:
                try:
                    ip_obj = ipaddress.ip_address(ip_value)
                except ValueError:
                    return False
                return any(ip_obj in network for network in INTERNAL_NETWORKS)

            source_internal = _is_internal_ip(source_ip)
            dest_internal = _is_internal_ip(dest_ip)
            
            return not source_internal and dest_internal
        
        # Generic rules require all specified recognized conditions to match.
        has_recognized_condition = False

        if "dest_port" in conditions:
            has_recognized_condition = True
            expected_port = conditions.get("dest_port")
            actual_port = dest.get("port")
            if actual_port is None or actual_port != expected_port:
                return False
        
        if "dest_ports" in conditions:
            has_recognized_condition = True
            port_list = conditions.get("dest_ports", [])
            actual_port = dest.get("port")
            if actual_port is None or actual_port not in port_list:
                return False
        
        if "event_type" in conditions:
            has_recognized_condition = True
            expected_type = conditions.get("event_type")
            actual_type = parsed_fields.get("event_type")
            if actual_type != expected_type:
                return False
        
        if "source_ip" in conditions:
            has_recognized_condition = True
            expected_ip = conditions.get("source_ip")
            actual_ip = source.get("ip")
            if actual_ip != expected_ip:
                return False

        return has_recognized_condition
    
    async def get_rule(self, rule_id: str) -> Rule | None:
        """Get a rule by ID."""
        result = await self.db.execute(
            select(Rule).where(Rule.rule_id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def list_rules(self, enabled_only: bool = True) -> list[Rule]:
        """List all rules."""
        query = select(Rule)
        if enabled_only:
            query = query.where(Rule.enabled == True)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_evaluations(self, processed_event_id: uuid.UUID) -> list[RuleEvaluation]:
        """Get all rule evaluations for a processed event."""
        result = await self.db.execute(
            select(RuleEvaluation).where(
                RuleEvaluation.processed_event_id == processed_event_id
            )
        )
        return list(result.scalars().all())

    async def create_rule(
        self,
        rule_id: str,
        name: str,
        category: str,
        conditions: dict[str, Any],
        severity: str,
        enabled: bool = True,
    ) -> Rule:
        """Create a new rule."""
        existing = await self.db.execute(select(Rule).where(Rule.rule_id == rule_id))
        if existing.scalar_one_or_none() is not None:
            raise ValueError(f"Rule with rule_id '{rule_id}' already exists")

        rule = Rule(
            rule_id=rule_id,
            name=name,
            category=category,
            conditions=conditions,
            severity=severity,
            enabled=enabled,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(rule)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            raise ValueError(f"Rule with rule_id '{rule_id}' already exists") from exc
        return rule

    async def get_all_rules(self) -> list[Rule]:
        """Get all rules (enabled and disabled)."""
        result = await self.db.execute(select(Rule))
        return list(result.scalars().all())

    async def toggle_rule(self, rule_id: uuid.UUID | str, active: bool) -> Rule | None:
        """Toggle a rule's enabled status."""
        # Support both UUID id and string rule_id
        if isinstance(rule_id, uuid.UUID):
            result = await self.db.execute(
                select(Rule).where(Rule.id == rule_id)
            )
        else:
            result = await self.db.execute(
                select(Rule).where(Rule.rule_id == rule_id)
            )
        
        rule = result.scalar_one_or_none()
        if rule:
            rule.enabled = active
            await self.db.flush()
        return rule
