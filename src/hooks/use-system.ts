// =============================================================================
// System Hooks - Health check and rules data fetching
// =============================================================================

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { HealthResponse, RuleResponse } from '@/types/api';

// -----------------------------------------------------------------------------
// Query Keys
// -----------------------------------------------------------------------------

export const systemKeys = {
  health: ['system', 'health'] as const,
  rules: ['system', 'rules'] as const,
  rule: (id: string) => ['system', 'rules', id] as const,
};

// -----------------------------------------------------------------------------
// Hooks
// -----------------------------------------------------------------------------

/**
 * Fetch system health status
 * Polls every 5 seconds for real-time status bar updates
 */
export function useHealth() {
  return useQuery({
    queryKey: systemKeys.health,
    queryFn: () => api.get<HealthResponse>('/api/v1/system/health', { skipAuth: true }),
    refetchInterval: 5000, // Poll every 5 seconds
    retry: 1,
    // Don't show loading state on refetch to prevent status bar flicker
    refetchOnWindowFocus: true,
  });
}

/**
 * Fetch all security rules
 */
export function useRules() {
  return useQuery({
    queryKey: systemKeys.rules,
    queryFn: () => api.get<RuleResponse[]>('/api/v1/system/rules'),
  });
}

/**
 * Fetch single rule by ID
 */
export function useRule(ruleId: string | undefined) {
  return useQuery({
    queryKey: systemKeys.rule(ruleId!),
    queryFn: () => api.get<RuleResponse>(`/api/v1/system/rules/${ruleId}`),
    enabled: !!ruleId,
  });
}
