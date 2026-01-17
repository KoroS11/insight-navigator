// =============================================================================
// Audit Hooks - Audit trail data fetching
// =============================================================================

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { AuditListResponse, AuditFilters, AuditEntryResponse } from '@/types/api';

// -----------------------------------------------------------------------------
// Query Keys
// -----------------------------------------------------------------------------

export const auditKeys = {
  all: ['audit'] as const,
  lists: () => [...auditKeys.all, 'list'] as const,
  list: (filters: AuditFilters) => [...auditKeys.lists(), filters] as const,
};

// -----------------------------------------------------------------------------
// Hooks
// -----------------------------------------------------------------------------

/**
 * Fetch paginated audit log entries
 * Polls every 5 seconds for real-time updates
 */
export function useAuditLog(filters: AuditFilters = {}) {
  const { limit = 50, offset = 0, entity_type, entity_id, user_id } = filters;

  const params = new URLSearchParams();
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  if (entity_type) params.set('entity_type', entity_type);
  if (entity_id) params.set('entity_id', entity_id);
  if (user_id) params.set('user_id', user_id);

  return useQuery({
    queryKey: auditKeys.list(filters),
    queryFn: async (): Promise<AuditListResponse> => {
      const entries = await api.get<AuditEntryResponse[]>(`/api/v1/audit?${params}`);
      // TODO: Backend should return total count in response headers or envelope
      // For now, total reflects current page length (pagination UI won't work correctly)
      return { entries, total: entries.length, limit, offset };
    },
    refetchInterval: 5000, // Poll every 5 seconds
  });
}
