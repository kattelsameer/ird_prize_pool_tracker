import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, buildQuery, type Paginated } from "./client";
import type { Coupon, CouponInput } from "./types";

export interface CouponFilters {
  search?: string;
  fiscal_year?: string;
  network?: string;
  match_status?: string;
  page?: number;
  page_size?: number;
}

export function couponsKey(filters: CouponFilters = {}) {
  return ["coupons", filters] as const;
}

export function useCoupons(filters: CouponFilters = {}) {
  return useQuery({
    queryKey: couponsKey(filters),
    queryFn: () =>
      api.get<Paginated<Coupon>>(
        `/api/coupons${buildQuery({
          search: filters.search,
          fiscal_year: filters.fiscal_year,
          network: filters.network,
          match_status: filters.match_status,
          page: filters.page ?? 1,
          page_size: filters.page_size ?? 20,
        })}`
      ),
    placeholderData: (prev) => prev,
  });
}

export function useCoupon(id: string | undefined) {
  return useQuery({
    queryKey: ["coupons", "detail", id],
    queryFn: () => api.get<Coupon>(`/api/coupons/${id}`),
    enabled: Boolean(id),
  });
}

export function useCreateCoupon() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CouponInput) => api.post<Coupon>("/api/coupons", input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coupons"] });
      queryClient.invalidateQueries({ queryKey: ["matches"] });
    },
  });
}

export function useUpdateCoupon(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CouponInput) => api.put<Coupon>(`/api/coupons/${id}`, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coupons"] });
      queryClient.invalidateQueries({ queryKey: ["matches"] });
    },
  });
}

export function useDeleteCoupon() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete<void>(`/api/coupons/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coupons"] });
      queryClient.invalidateQueries({ queryKey: ["matches"] });
    },
  });
}
