import { useQuery } from "@tanstack/react-query";
import { api, buildQuery, type Paginated } from "./client";
import type { PrizePool } from "./types";

export interface PrizePoolFilters {
  fiscal_year?: string;
  category?: string;
  coupon_code?: string;
  claim_status?: string;
  date_from?: string;
  date_to?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}

export function usePrizePools(filters: PrizePoolFilters = {}) {
  const pageSize = filters.page_size ?? 20;
  const page = filters.page ?? 1;
  return useQuery({
    queryKey: ["prize-pools", filters],
    queryFn: () =>
      // The backend paginates by limit/offset, not page number (app/api/prize_pools.py);
      // page/page_size here is just a friendlier shape for the UI to think in.
      api.get<Paginated<PrizePool>>(
        `/api/prize-pools${buildQuery({
          fiscal_year: filters.fiscal_year,
          category: filters.category,
          coupon_code: filters.coupon_code,
          claim_status: filters.claim_status,
          date_from: filters.date_from,
          date_to: filters.date_to,
          sort: filters.sort,
          limit: pageSize,
          offset: (page - 1) * pageSize,
        })}`
      ),
    placeholderData: (prev) => prev,
  });
}

export function usePrizePool(id: string | undefined) {
  return useQuery({
    queryKey: ["prize-pools", "detail", id],
    queryFn: () => api.get<PrizePool>(`/api/prize-pools/${id}`),
    enabled: Boolean(id),
  });
}
