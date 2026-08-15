import { useEffect, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type { SyncStatus, SyncTriggerResponse } from "./types";

const KEY = ["sync", "status"] as const;

export function useSyncStatus() {
  const queryClient = useQueryClient();
  const wasRunning = useRef(false);

  const query = useQuery({
    queryKey: KEY,
    queryFn: () => api.get<SyncStatus>("/api/sync/status"),
    // Poll quickly while a sync is actually running so "Syncing..." clears the
    // moment it finishes, instead of leaving the user staring at a stale
    // status for up to a full 30s interval.
    refetchInterval: (q) => (q.state.data?.is_running ? 2_000 : 30_000),
  });

  // The sync itself runs in a background thread (fire-and-forget from the
  // trigger's point of view), so the moment data actually changes is when
  // is_running flips from true back to false here -- not when the trigger
  // click resolves. Refresh everything the sync could have affected right
  // at that transition, whether the sync was started by this user clicking
  // "Sync now" or by the daily scheduled cron running in the background.
  useEffect(() => {
    const isRunning = query.data?.is_running ?? false;
    if (wasRunning.current && !isRunning) {
      queryClient.invalidateQueries({ queryKey: ["prize-pools"] });
      queryClient.invalidateQueries({ queryKey: ["matches"] });
      queryClient.invalidateQueries({ queryKey: ["wins"] });
      queryClient.invalidateQueries({ queryKey: ["claims"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    }
    wasRunning.current = isRunning;
  }, [query.data?.is_running, queryClient]);

  return query;
}

export function useTriggerSync() {
  const queryClient = useQueryClient();
  return useMutation({
    // POST /api/sync returns a SyncTriggerResponse ({accepted, message}), not a
    // SyncStatus -- the sync itself runs in a background thread, so this call
    // only confirms whether a run just started (or one was already in
    // progress). Writing this shape into the sync-status cache directly (as a
    // previous version of this hook did) corrupted `is_running`/`latest_run`
    // until the next poll overwrote it, which is why "Sync now" appeared to
    // do nothing for a few seconds after every click.
    mutationFn: () => api.post<SyncTriggerResponse>("/api/sync"),
    onSuccess: () => {
      // Refresh the real status immediately rather than waiting for the next
      // poll -- this is what actually flips the UI to "Syncing..." right away.
      queryClient.invalidateQueries({ queryKey: KEY });
    },
  });
}
