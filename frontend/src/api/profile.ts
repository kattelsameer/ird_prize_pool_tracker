import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type { Profile } from "./types";

const KEY = ["profile"] as const;

export function useProfile() {
  return useQuery({
    queryKey: KEY,
    queryFn: () => api.get<Profile>("/api/profile"),
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<Pick<Profile, "display_name">>) =>
      api.put<Profile>("/api/profile", input),
    onSuccess: (data) => {
      queryClient.setQueryData(KEY, data);
    },
  });
}
