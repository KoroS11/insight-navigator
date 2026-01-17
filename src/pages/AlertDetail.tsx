// =============================================================================
// AlertDetail Page - Consolidated view for alert analysis and decisions
// =============================================================================

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAlert } from '@/hooks/use-alerts';
import { useCreateDecision } from '@/hooks/use-decisions';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  ArrowLeft,
  Shield,
  AlertTriangle,
  CheckCircle,
  Eye,
  Clock,
  Network,
  Activity,
  FileText,
  History,
  Loader2,
} from 'lucide-react';
import type { DecisionAction, Severity, AlertClassification } from '@/types/api';

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

function getRiskColor(score: number): string {
  if (score >= 70) return 'text-red-500';
  if (score >= 40) return 'text-yellow-500';
  return 'text-green-500';
}

function getClassificationVariant(classification: AlertClassification): 'destructive' | 'default' | 'secondary' {
  switch (classification) {
    case 'HIGH': return 'destructive';
    case 'MEDIUM': return 'default';
    case 'LOW': return 'secondary';
  }
}

function getSeverityColor(severity: Severity): string {
  switch (severity) {
    case 'HIGH': return 'text-red-500';
    case 'MEDIUM': return 'text-yellow-500';
    case 'LOW': return 'text-green-500';
  }
}

function formatTimestamp(ts: string): string {
  return new Date(ts).toLocaleString();
}

// -----------------------------------------------------------------------------
// Loading Skeleton
// -----------------------------------------------------------------------------

function AlertDetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10" />
        <Skeleton className="h-8 w-64" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
      </div>
      <Skeleton className="h-64" />
    </div>
  );
}

// -----------------------------------------------------------------------------
// Decision Form Component
// -----------------------------------------------------------------------------

interface DecisionFormProps {
  alertId: string;
  currentStatus: string;
}

function DecisionForm({ alertId, currentStatus }: DecisionFormProps) {
  const [action, setAction] = useState<DecisionAction | null>(null);
  const [justification, setJustification] = useState('');
  const { mutate: createDecision, isPending } = useCreateDecision(alertId);

  const actions: { value: DecisionAction; label: string; icon: React.ReactNode; description: string }[] = [
    { value: 'ESCALATE', label: 'Escalate', icon: <AlertTriangle className="h-4 w-4" />, description: 'Escalate to senior analyst or SOC team' },
    { value: 'DISMISS', label: 'Dismiss', icon: <CheckCircle className="h-4 w-4" />, description: 'False positive - no action needed' },
    { value: 'MARK_SAFE', label: 'Mark Safe', icon: <Shield className="h-4 w-4" />, description: 'Verified benign activity' },
    { value: 'WATCH', label: 'Watch', icon: <Eye className="h-4 w-4" />, description: 'Monitor for further activity' },
  ];

  const handleSubmit = () => {
    if (!action || justification.length < 10) return;
    
    createDecision(
      {
        action,
        justification,
        follow_up_required: action === 'WATCH' || action === 'ESCALATE',
      },
      {
        onSuccess: () => {
          // Reset form only after successful submission
          setAction(null);
          setJustification('');
        },
      }
    );
  };

  const isResolved = ['RESOLVED', 'DISMISSED'].includes(currentStatus);

  if (isResolved) {
    return (
      <Alert>
        <CheckCircle className="h-4 w-4" />
        <AlertTitle>Alert Resolved</AlertTitle>
        <AlertDescription>
          This alert has been resolved. You can still add additional decisions if needed.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {actions.map((a) => (
          <Button
            key={a.value}
            variant={action === a.value ? 'default' : 'outline'}
            className="flex flex-col h-auto py-3 gap-1"
            onClick={() => setAction(a.value)}
            disabled={isPending}
          >
            {a.icon}
            <span className="font-medium">{a.label}</span>
            <span className="text-xs text-muted-foreground hidden md:block">{a.description}</span>
          </Button>
        ))}
      </div>

      {action && (
        <>
          <div className="space-y-2">
            <Label htmlFor="justification">
              Justification <span className="text-muted-foreground">(min 10 characters)</span>
            </Label>
            <Textarea
              id="justification"
              placeholder="Explain your decision..."
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              rows={3}
              disabled={isPending}
            />
          </div>

          <Button
            onClick={handleSubmit}
            disabled={isPending || justification.length < 10}
            className="w-full"
          >
            {isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              `Submit ${action.replace('_', ' ')}`
            )}
          </Button>
        </>
      )}
    </div>
  );
}

// -----------------------------------------------------------------------------
// Main Component
// -----------------------------------------------------------------------------

export default function AlertDetail() {
  const { alertId } = useParams<{ alertId: string }>();
  const navigate = useNavigate();
  const { data: alert, isLoading, error } = useAlert(alertId);

  if (isLoading) {
    return (
      <div className="container py-6">
        <AlertDetailSkeleton />
      </div>
    );
  }

  if (error || !alert) {
    return (
      <div className="container py-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error?.message || 'Alert not found'}
          </AlertDescription>
        </Alert>
        <Button variant="ghost" onClick={() => navigate(-1)} className="mt-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Go Back
        </Button>
      </div>
    );
  }

  const event = alert.event;
  const detection = alert.neural_detection;
  const explanation = alert.explanation?.explanation_data;

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">Alert Analysis</h1>
            <Badge variant={getClassificationVariant(alert.classification)}>
              {alert.classification}
            </Badge>
            <Badge variant="outline">{alert.status}</Badge>
          </div>
          <p className="text-muted-foreground text-sm">
            {alert.id} • Created {formatTimestamp(alert.created_at)}
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Risk Score */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Risk Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-4xl font-bold ${getRiskColor(alert.composite_risk_score)}`}>
              {alert.composite_risk_score}
              <span className="text-lg text-muted-foreground">/100</span>
            </div>
          </CardContent>
        </Card>

        {/* Event Info */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Network className="h-4 w-4" />
              Network
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div><span className="text-muted-foreground">Source:</span> {event?.source_ip || 'N/A'}</div>
            <div><span className="text-muted-foreground">Dest:</span> {event?.dest_ip}{event?.dest_port != null ? `:${event.dest_port}` : ''}</div>
            <div><span className="text-muted-foreground">Protocol:</span> {event?.protocol}</div>
          </CardContent>
        </Card>

        {/* Timestamp */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Timestamp
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div><span className="text-muted-foreground">Event:</span> {event ? formatTimestamp(event.timestamp) : 'N/A'}</div>
            <div><span className="text-muted-foreground">Alert:</span> {formatTimestamp(alert.created_at)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabbed Content */}
      <Tabs defaultValue="explanation" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="explanation">
            <FileText className="h-4 w-4 mr-2" />
            Explanation
          </TabsTrigger>
          <TabsTrigger value="detection">
            <Activity className="h-4 w-4 mr-2" />
            Detection
          </TabsTrigger>
          <TabsTrigger value="decision">
            <Shield className="h-4 w-4 mr-2" />
            Decision
          </TabsTrigger>
          <TabsTrigger value="history">
            <History className="h-4 w-4 mr-2" />
            History
          </TabsTrigger>
        </TabsList>

        {/* Explanation Tab */}
        <TabsContent value="explanation" className="space-y-4">
          {explanation?.natural_language || explanation?.summary ? (
            <Card>
              <CardHeader>
                <CardTitle>Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{explanation.natural_language || explanation.summary}</p>
              </CardContent>
            </Card>
          ) : null}

          {/* Rules Triggered */}
          {explanation?.rules_triggered && explanation.rules_triggered.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Rules Triggered</CardTitle>
                <CardDescription>{explanation.rules_triggered.length} rules matched</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {explanation.rules_triggered.map((rule, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 border rounded-lg">
                      <Badge variant={rule.severity === 'HIGH' ? 'destructive' : 'default'}>
                        {rule.severity}
                      </Badge>
                      <div>
                        <div className="font-medium">{rule.name}</div>
                        <div className="text-sm text-muted-foreground">{rule.why_matched}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Counterfactuals */}
          {explanation?.counterfactuals && explanation.counterfactuals.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>What-If Analysis</CardTitle>
                <CardDescription>Conditions that would change the outcome</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {explanation.counterfactuals.map((cf, idx) => (
                    <div key={idx} className="p-3 border rounded-lg">
                      <div className="font-medium">{cf.condition}</div>
                      <div className="text-sm text-muted-foreground">{cf.impact}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Detection Tab */}
        <TabsContent value="detection">
          <Card>
            <CardHeader>
              <CardTitle>Anomaly Scores</CardTitle>
              <CardDescription>Neural detection analysis breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              {detection ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { label: 'Frequency', score: detection.frequency_score },
                      { label: 'Port', score: detection.port_score },
                      { label: 'Temporal', score: detection.temporal_score },
                      { label: 'Geographic', score: detection.geographic_score },
                    ].map((item) => (
                      <div key={item.label} className="text-center p-4 border rounded-lg">
                        <div className="text-2xl font-bold">{Math.round(item.score * 100)}%</div>
                        <div className="text-sm text-muted-foreground">{item.label}</div>
                      </div>
                    ))}
                  </div>
                  <Separator />
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Composite Anomaly Score</span>
                    <span className="text-2xl font-bold">{Math.round(detection.anomaly_score * 100)}%</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Model: {detection.model_version}
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">No detection data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Decision Tab */}
        <TabsContent value="decision">
          <Card>
            <CardHeader>
              <CardTitle>Make a Decision</CardTitle>
              <CardDescription>Choose an action and provide justification</CardDescription>
            </CardHeader>
            <CardContent>
              <DecisionForm alertId={alert.id} currentStatus={alert.status} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Decision History</CardTitle>
              <CardDescription>All decisions made on this alert</CardDescription>
            </CardHeader>
            <CardContent>
              {alert.decisions && alert.decisions.length > 0 ? (
                <div className="space-y-4">
                  {alert.decisions.map((decision) => (
                    <div key={decision.id} className="p-4 border rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <Badge>{decision.action}</Badge>
                        <span className="text-sm text-muted-foreground">
                          {formatTimestamp(decision.decision_timestamp)}
                        </span>
                      </div>
                      <p className="text-sm">{decision.justification}</p>
                      <div className="text-xs text-muted-foreground">
                        Analyst: {decision.analyst_id}
                        {decision.follow_up_required && (
                          <span className="ml-2">• Follow-up required</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No decisions recorded yet</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
