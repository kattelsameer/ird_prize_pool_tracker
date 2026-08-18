import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, clearStoredToken, getStoredToken, setStoredToken } from "./client";
import type { AuthResponse, User } from "./types";

export const ME_KEY = ["auth", "me"] as const;

export function useCurrentUser() {
  return useQuery({
    queryKey: ME_KEY,
    queryFn: () => api.get<User>("/api/auth/me"),
    enabled: Boolean(getStoredToken()),
    retry: false,
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (input: { email: string; password: string }) =>
      api.post<AuthResponse>("/api/auth/register", input),
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { email: string; password: string }) =>
      api.post<AuthResponse>("/api/auth/login", input),
    onSuccess: (data) => {
      setStoredToken(data.access_token);
      queryClient.setQueryData(ME_KEY, data.user);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return () => {
    clearStoredToken();
    // Wipe every cached query -- coupons/notifications/settings all belong to
    // the account that just logged out; the next login must not show stale
    // data from a previous session in the same browser tab.
    queryClient.clear();
  };
}
