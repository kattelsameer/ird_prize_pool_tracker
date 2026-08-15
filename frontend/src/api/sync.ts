import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type { SyncStatus } from "./types";

const KEY = ["sync", "status"] as const;

export function useSyncStatus() {
  return useQuery({
    queryKey: KEY,
    queryFn: () => api.get<SyncStatus>("/api/sync/status"),
    refetchInterval: 30_000,
  });
}

export function useTriggerSync() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.post<SyncStatus>("/api/sync"),
    onSuccess: (data) => {
      queryClient.setQueryData(KEY, data);
      queryClient.invalidateQueries({ queryKey: ["prize-pools"] });
      queryClient.invalidateQueries({ queryKey: ["matches"] });
      queryClient.invalidateQueries({ queryKey: ["wins"] });
      queryClient.invalidateQueries({ queryKey: ["claims"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
