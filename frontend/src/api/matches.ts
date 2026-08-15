import { useQuery } from "@tanstack/react-query";
import { api } from "./client";
import type { MatchResult } from "./types";

export function useMatches() {
  return useQuery({
    queryKey: ["matches"],
    queryFn: () => api.get<MatchResult[]>("/api/matches"),
  });
}

export function useWins() {
  return useQuery({
    queryKey: ["wins"],
    queryFn: () => api.get<MatchResult[]>("/api/wins"),
  });
}

export function useClaims() {
  return useQuery({
    queryKey: ["claims"],
    // /api/claims returns the same flat MatchRead[] shape as /matches and /wins
    // (app/api/matches.py), not raw PrizePoolWinner records.
    queryFn: () => api.get<MatchResult[]>("/api/claims"),
  });
}
