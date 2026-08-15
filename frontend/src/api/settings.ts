import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type { Network, Settings, SettingsUpdate } from "./types";

const KEY = ["settings"] as const;

export function useSettings() {
  return useQuery({
    queryKey: KEY,
    queryFn: () => api.get<Settings>("/api/settings"),
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    // PUT /api/settings only accepts the notify_* flags (app/schemas/settings.py's
    // SettingsUpdate) -- networks are managed through their own endpoints below.
    mutationFn: (input: SettingsUpdate) => api.put<Settings>("/api/settings", input),
    onSuccess: (data) => queryClient.setQueryData(KEY, data),
  });
}

export function useAddNetwork() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => api.post<Network>("/api/settings/networks", { name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}

export function useUpdateNetwork() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...input }: { id: string; name?: string; active?: boolean }) =>
      api.patch<Network>(`/api/settings/networks/${id}`, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}
