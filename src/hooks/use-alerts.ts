// =============================================================================
// Alerts Hooks - Data fetching for security alerts
// =============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type {
  AlertResponse,
  AlertDetailResponse,
  AlertListResponse,
  AlertFilters,
  AlertStatus,
  AlertStatusUpdate,
} from '@/types/api';

// -----------------------------------------------------------------------------
// Query Keys
// -----------------------------------------------------------------------------

export const alertKeys = {
  all: ['alerts'] as const,
  lists: () => [...alertKeys.all, 'list'] as const,
  list: (filters: AlertFilters) => [...alertKeys.lists(), filters] as const,
  details: () => [...alertKeys.all, 'detail'] as const,
  detail: (id: string) => [...alertKeys.details(), id] as const,
};

// -----------------------------------------------------------------------------
// Hooks
// -----------------------------------------------------------------------------

/**
 * Fetch paginated list of alerts with optional filters
 * Polls every 5 seconds for real-time updates
 */
export function useAlerts(filters: AlertFilters = {}) {
  const { limit = 20, offset = 0, status, classification } = filters;

  const params = new URLSearchParams();
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  if (status) params.set('status', status);
  if (classification) params.set('classification', classification);

  return useQuery({
    queryKey: alertKeys.list(filters),
    queryFn: async (): Promise<AlertListResponse> => {
      const alerts = await api.get<AlertResponse[]>(`/api/v1/alerts?${params}`);
      // TODO: Backend should return total count in response headers or envelope
      // For now, total reflects current page length (pagination UI won't work correctly)
      return { alerts, total: alerts.length, limit, offset };
    },
    refetchInterval: 5000, // Poll every 5 seconds
  });
}

/**
 * Fetch single alert with full context (event, detection, explanation, decisions)
 */
export function useAlert(alertId: string | undefined) {
  return useQuery({
    queryKey: alertKeys.detail(alertId!),
    queryFn: () => api.get<AlertDetailResponse>(`/api/v1/alerts/${alertId}`),
    enabled: !!alertId,
  });
}

/**
 * Update alert status (PENDING, ESCALATED, DISMISSED, RESOLVED)
 */
export function useUpdateAlertStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ alertId, status }: { alertId: string; status: AlertStatus }) =>
      api.patch<AlertResponse>(`/api/v1/alerts/${alertId}/status`, { status } as AlertStatusUpdate),
    onSuccess: (data, { alertId }) => {
      // Update the specific alert in cache
      queryClient.setQueryData(alertKeys.detail(alertId), (old: AlertDetailResponse | undefined) => {
        if (!old) return old;
        return { ...old, status: data.status, updated_at: data.updated_at };
      });
      // Invalidate lists to reflect status change
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
    },
  });
}

/**
 * Get count of pending alerts (for dashboard)
 */
export function usePendingAlertCount() {
  return useQuery({
    queryKey: [...alertKeys.list({ status: 'PENDING' as AlertStatus, limit: 1 }), 'count'],
    queryFn: async () => {
      const alerts = await api.get<AlertResponse[]>('/api/v1/alerts?status=PENDING');
      return alerts.length;
    },
    refetchInterval: 5000,
  });
}
