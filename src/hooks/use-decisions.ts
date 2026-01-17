// =============================================================================
// Decisions Hooks - Analyst decision submission with optimistic updates
// =============================================================================

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { alertKeys } from '@/hooks/use-alerts';
import type {
  DecisionRequest,
  DecisionResponse,
  AlertDetailResponse,
} from '@/types/api';

// -----------------------------------------------------------------------------
// Hooks
// -----------------------------------------------------------------------------

/**
 * Create a new decision for an alert with optimistic updates
 * 
 * The decision appears immediately in the UI, then syncs with server.
 * On error, rolls back to previous state and shows toast.
 */
export function useCreateDecision(alertId: string) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (decision: DecisionRequest) =>
      api.post<DecisionResponse>(`/api/v1/alerts/${alertId}/decisions`, decision),

    // Optimistic update - immediately show the decision
    onMutate: async (newDecision) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: alertKeys.detail(alertId) });

      // Snapshot previous value
      const previousAlert = queryClient.getQueryData<AlertDetailResponse>(
        alertKeys.detail(alertId)
      );

      // Optimistically update with temporary decision
      if (previousAlert) {
        const optimisticDecision: DecisionResponse = {
          id: `temp-${Date.now()}`,
          alert_id: alertId,
          analyst_id: 'current-user', // Will be replaced by server
          action: newDecision.action,
          justification: newDecision.justification,
          follow_up_required: newDecision.follow_up_required ?? false,
          follow_up_deadline: newDecision.follow_up_hours
            ? new Date(Date.now() + newDecision.follow_up_hours * 60 * 60 * 1000).toISOString()
            : null,
          decision_timestamp: new Date().toISOString(),
          ip_address: null,
          user_agent: null,
        };

        // Determine new status based on action
        const statusMap: Record<string, string> = {
          ESCALATE: 'ESCALATED',
          DISMISS: 'RESOLVED',
          MARK_SAFE: 'DISMISSED',
          WATCH: 'PENDING',
        };

        queryClient.setQueryData<AlertDetailResponse>(
          alertKeys.detail(alertId),
          {
            ...previousAlert,
            status: (statusMap[newDecision.action] ?? 'PENDING') as AlertDetailResponse['status'],
            decisions: [...(previousAlert.decisions || []), optimisticDecision],
          }
        );
      }

      return { previousAlert };
    },

    // On error, rollback to previous state
    onError: (err, _newDecision, context) => {
      if (context?.previousAlert) {
        queryClient.setQueryData(
          alertKeys.detail(alertId),
          context.previousAlert
        );
      }

      toast({
        variant: 'destructive',
        title: 'Failed to submit decision',
        description: err instanceof Error ? err.message : 'An error occurred',
      });
    },

    // On success, show confirmation and sync with server
    onSuccess: (data) => {
      const actionMessages: Record<string, string> = {
        ESCALATE: 'escalated',
        DISMISS: 'dismissed',
        MARK_SAFE: 'marked as safe',
        WATCH: 'set to watch',
      };
      toast({
        title: 'Decision recorded',
        description: `Alert ${actionMessages[data.action] ?? data.action.toLowerCase()} successfully.`,
      });
    },

    // Always refetch after error or success to sync with server
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: alertKeys.detail(alertId) });
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
    },
  });
}
