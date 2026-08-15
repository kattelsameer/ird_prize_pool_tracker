import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type Paginated } from "./client";
import type { AppNotification } from "./types";

const KEY = ["notifications"] as const;

export function useNotifications() {
  return useQuery({
    queryKey: KEY,
    // GET /api/notifications returns a paginated Page[NotificationRead] (app/api/notifications.py),
    // not a bare array -- callers read `.data?.items`.
    queryFn: () => api.get<Paginated<AppNotification>>("/api/notifications?limit=50"),
    refetchInterval: 60_000,
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.post<void>(`/api/notifications/${id}/read`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.post<void>("/api/notifications/read-all"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}
