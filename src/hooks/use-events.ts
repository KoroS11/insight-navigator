// =============================================================================
// Events Hooks - Data fetching for security events
// =============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type {
  EventResponse,
  EventListResponse,
  EventFilters,
  EventCreate,
  PipelineResultResponse,
  ProcessedEventResponse,
} from '@/types/api';

// -----------------------------------------------------------------------------
// Query Keys
// -----------------------------------------------------------------------------

export const eventKeys = {
  all: ['events'] as const,
  lists: () => [...eventKeys.all, 'list'] as const,
  list: (filters: EventFilters) => [...eventKeys.lists(), filters] as const,
  details: () => [...eventKeys.all, 'detail'] as const,
  detail: (id: string) => [...eventKeys.details(), id] as const,
  processed: (id: string) => [...eventKeys.detail(id), 'processed'] as const,
};

// -----------------------------------------------------------------------------
// Hooks
// -----------------------------------------------------------------------------

/**
 * Fetch paginated list of events with optional filters
 */
export function useEvents(filters: EventFilters = {}) {
  const { limit = 20, offset = 0, event_type, start_time, end_time } = filters;

  const params = new URLSearchParams();
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  if (event_type) params.set('event_type', event_type);
  if (start_time) params.set('start_time', start_time);
  if (end_time) params.set('end_time', end_time);

  return useQuery({
    queryKey: eventKeys.list(filters),
    queryFn: async (): Promise<EventListResponse> => {
      const events = await api.get<EventResponse[]>(`/api/v1/events?${params}`);
      // TODO: Backend should return total count in response headers or envelope
      // For now, total reflects current page length (pagination UI won't work correctly)
      return { events, total: events.length, limit, offset };
    },
  });
}

/**
 * Fetch single event by ID
 */
export function useEvent(eventId: string | undefined) {
  return useQuery({
    queryKey: eventKeys.detail(eventId!),
    queryFn: () => api.get<EventResponse>(`/api/v1/events/${eventId}`),
    enabled: !!eventId,
  });
}

/**
 * Fetch processed event data for an event
 */
export function useProcessedEvent(eventId: string | undefined) {
  return useQuery({
    queryKey: eventKeys.processed(eventId!),
    queryFn: () => api.get<ProcessedEventResponse>(`/api/v1/events/${eventId}/processed`),
    enabled: !!eventId,
  });
}

/**
 * Ingest a new event (triggers full pipeline)
 */
export function useIngestEvent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (event: EventCreate) =>
      api.post<PipelineResultResponse>('/api/v1/events', event),
    onSuccess: () => {
      // Invalidate events list to show new event
      queryClient.invalidateQueries({ queryKey: eventKeys.lists() });
    },
  });
}
