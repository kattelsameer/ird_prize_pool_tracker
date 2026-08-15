import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type { Settings } from "./types";

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
    mutationFn: (input: Settings) => api.put<Settings>("/api/settings", input),
    onSuccess: (data) => queryClient.setQueryData(KEY, data),
  });
}
