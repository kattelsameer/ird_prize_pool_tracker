import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, buildQuery, type Paginated } from "./client";
import type { Coupon, CouponInput } from "./types";

export interface CouponFilters {
  search?: string;
  fiscal_year?: string;
  network?: string;
  page?: number;
  page_size?: number;
}

export function couponsKey(filters: CouponFilters = {}) {
  return ["coupons", filters] as const;
}

export function useCoupons(filters: CouponFilters = {}) {
  const pageSize = filters.page_size ?? 20;
  const page = filters.page ?? 1;
  return useQuery({
    queryKey: couponsKey(filters),
    queryFn: () =>
      // The backend paginates by limit/offset, not page number (app/api/coupons.py);
      // page/page_size here is just a friendlier shape for the UI to think in.
      api.get<Paginated<Coupon>>(
        `/api/coupons${buildQuery({
          search: filters.search,
          fiscal_year: filters.fiscal_year,
          network: filters.network,
          limit: pageSize,
          offset: (page - 1) * pageSize,
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
