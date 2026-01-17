// =============================================================================
// API Types - TypeScript interfaces matching backend Pydantic schemas
// =============================================================================

// -----------------------------------------------------------------------------
// Error Types
// -----------------------------------------------------------------------------

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(`${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

// -----------------------------------------------------------------------------
// Auth Types
// -----------------------------------------------------------------------------

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface UserResponse {
  id: string;
  username: string;
  full_name: string | null;
  role: 'analyst' | 'admin';
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// -----------------------------------------------------------------------------
// Event Types (Layer 1)
// -----------------------------------------------------------------------------

export interface EventResponse {
  id: string;
  timestamp: string;
  source_ip: string;
  dest_ip: string;
  source_port: number | null;
  dest_port: number | null;
  protocol: string;
  event_type: string;
  raw_data: Record<string, unknown>;
  created_at: string;
}

export interface EventCreate {
  event_type: string;
  source_ip: string;
  dest_ip: string;
  dest_port: number;
  protocol: string;
  timestamp: string;
  raw_data: Record<string, unknown>;
}

export interface EventListResponse {
  events: EventResponse[];
  total: number;
  limit: number;
  offset: number;
}

// -----------------------------------------------------------------------------
// Processed Event Types (Layer 2)
// -----------------------------------------------------------------------------

export interface ProcessedEventResponse {
  id: string;
  event_id: string;
  parsed_fields: {
    network: {
      source: { ip: string; port: number | null };
      destination: { ip: string; port: number | null };
      protocol: string;
    };
    temporal: {
      timestamp: string;
      hour_of_day: number;
      day_of_week: number;
      is_business_hours: boolean;
    };
    asset: {
      hostname: string;
      criticality: number;
    };
  };
  asset_hostname: string;
  asset_criticality: number;
  event_hash: string;
  processing_timestamp: string;
  processing_duration_ms: number;
}

// -----------------------------------------------------------------------------
// Neural Detection Types (Layer 3)
// -----------------------------------------------------------------------------

export interface NeuralDetectionResponse {
  id: string;
  processed_event_id: string;
  anomaly_score: number;
  frequency_score: number;
  port_score: number;
  temporal_score: number;
  geographic_score: number;
  detection_timestamp: string;
  model_version: string;
}

// -----------------------------------------------------------------------------
// Rule Types (Layer 4)
// -----------------------------------------------------------------------------

export type Severity = 'LOW' | 'MEDIUM' | 'HIGH';

export interface RuleResponse {
  rule_id: string;
  name: string;
  category: string;
  conditions: Record<string, unknown>;
  severity: Severity;
  enabled: boolean;
  created_at: string;
}

export interface RuleEvaluationResponse {
  id: string;
  processed_event_id: string;
  rule_id: string;
  matched: boolean;
  severity: Severity | null;
}

// -----------------------------------------------------------------------------
// Alert Types (Layer 5)
// -----------------------------------------------------------------------------

export type AlertStatus = 'PENDING' | 'ESCALATED' | 'DISMISSED' | 'RESOLVED';
export type AlertClassification = 'LOW' | 'MEDIUM' | 'HIGH';

export interface AlertResponse {
  id: string;
  event_id: string;
  processed_event_id: string;
  neural_detection_id: string | null;
  composite_risk_score: number;
  classification: AlertClassification;
  alert_category: string | null;
  status: AlertStatus;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertDetailResponse extends AlertResponse {
  event?: EventResponse;
  processed_event?: ProcessedEventResponse;
  neural_detection?: NeuralDetectionResponse;
  rule_evaluations?: RuleEvaluationResponse[];
  explanation?: ExplanationResponse;
  decisions: DecisionResponse[];
}

export interface AlertListResponse {
  alerts: AlertResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface AlertStatusUpdate {
  status: AlertStatus;
}

// -----------------------------------------------------------------------------
// Explanation Types (Layer 6)
// -----------------------------------------------------------------------------

export interface ExplanationTreeNode {
  type: 'alert' | 'neural_detection' | 'symbolic_reasoning' | 'factor' | 'rule_match';
  classification?: AlertClassification;
  composite_risk_score?: number;
  anomaly_score?: number;
  rules_matched?: number;
  name?: string;
  score?: number;
  rule_id?: string;
  severity?: Severity;
  children?: ExplanationTreeNode[];
}

export interface Counterfactual {
  type: string;
  condition: string;
  impact: string;
  potential_reduction: number;
}

export interface EvidenceFactor {
  type: string;
  factor: string;
  weight: string;
  detail: string;
  score: number | null;
}

export interface RuleTriggered {
  rule_id: string;
  name: string;
  severity: Severity;
  why_matched: string;
}

export interface ExplanationData {
  tree?: {
    root: ExplanationTreeNode;
  };
  summary?: string;
  natural_language?: string;
  risk_assessment?: Record<string, unknown>;
  evidence?: Record<string, EvidenceFactor[]>;
  rules_triggered?: RuleTriggered[];
  historical_context?: Record<string, unknown>;
  counterfactuals?: Counterfactual[];
}

export interface ExplanationResponse {
  id: string;
  alert_id: string;
  explanation_data: ExplanationData;
  generated_at: string;
  generation_duration_ms: number | null;
}

// -----------------------------------------------------------------------------
// Decision Types (Layer 7)
// -----------------------------------------------------------------------------

export type DecisionAction = 'ESCALATE' | 'DISMISS' | 'MARK_SAFE' | 'WATCH';

export interface DecisionRequest {
  action: DecisionAction;
  justification: string;
  follow_up_required?: boolean;
  follow_up_hours?: number;
}

export interface DecisionResponse {
  id: string;
  alert_id: string;
  analyst_id: string;
  action: DecisionAction;
  justification: string;
  follow_up_required: boolean;
  follow_up_deadline: string | null;
  decision_timestamp: string;
  ip_address: string | null;
  user_agent: string | null;
}

// -----------------------------------------------------------------------------
// Audit Types
// -----------------------------------------------------------------------------

export interface AuditEntryResponse {
  id: string;
  event_type: string;
  actor: string;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  result: string;
  metadata: Record<string, unknown> | null;
  timestamp: string;
  ip_address: string | null;
}

export interface AuditListResponse {
  entries: AuditEntryResponse[];
  total: number;
  limit: number;
  offset: number;
}

// -----------------------------------------------------------------------------
// System Types
// -----------------------------------------------------------------------------

export interface HealthResponse {
  status: string;
  timestamp: string;
  version?: string;
  metrics?: {
    database?: string;
    uptime_seconds?: number;
    events_processed_24h?: number;
    alerts_pending?: number;
  };
}

// -----------------------------------------------------------------------------
// Pipeline Types
// -----------------------------------------------------------------------------

export interface PipelineResultResponse {
  event_id: string;
  processed_event_id: string | null;
  anomaly_score: number | null;
  rules_matched: string[];
  alert_id: string | null;
  explanation_id: string | null;
  risk_score: number | null;
  classification: AlertClassification | null;
  processing_time_ms: number | null;
  status: string;
  message: string | null;
}

// -----------------------------------------------------------------------------
// Query Filter Types
// -----------------------------------------------------------------------------

export interface EventFilters {
  limit?: number;
  offset?: number;
  event_type?: string;
  start_time?: string;
  end_time?: string;
}

export interface AlertFilters {
  limit?: number;
  offset?: number;
  status?: AlertStatus;
  classification?: AlertClassification;
}

export interface AuditFilters {
  limit?: number;
  offset?: number;
  entity_type?: string;
  entity_id?: string;
  user_id?: string;
}
