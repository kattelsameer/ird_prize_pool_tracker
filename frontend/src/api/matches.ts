import { useQuery } from "@tanstack/react-query";
import { api } from "./client";
import type { MatchResult, PrizePool } from "./types";

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
    queryFn: () => api.get<PrizePool[]>("/api/claims"),
  });
}
