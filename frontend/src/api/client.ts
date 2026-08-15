/**
 * Thin fetch wrapper shared by every API module.
 *
 * - Base URL comes from VITE_API_BASE_URL (empty string in the production Docker image,
 *   where nginx reverse-proxies /api/* to the backend container on the same origin).
 * - Never throws raw fetch/parse errors to the UI layer un-annotated: callers get an
 *   ApiError with a user-safe `message` plus the original `cause` for console logging only.
 * - Never logs personal data; only method/path/status.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  status?: number;
  cause?: unknown;

  constructor(message: string, opts?: { status?: number; cause?: unknown }) {
    super(message);
    this.name = "ApiError";
    this.status = opts?.status;
    this.cause = opts?.cause;
  }
}

// Mirrors the backend's Page[T] schema (app/schemas/common.py) exactly: offset-based
// pagination, not page-number-based. Callers that think in "page N of size S" (the page
// components do, for a friendlier UI) convert to limit/offset at the query-building edge.
export interface Paginated<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

type QueryValue = string | number | boolean | undefined | null;

export function buildQuery(params: Record<string, QueryValue>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    search.set(key, String(value));
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch (err) {
    // Network-level failure (offline, DNS, connection refused, etc).
    console.error(`API request failed (network): ${init?.method ?? "GET"} ${path}`, err);
    throw new ApiError(
      "We couldn't reach the server. Check your connection and try again.",
      { cause: err }
    );
  }

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body = await response.json();
      detail = typeof body?.detail === "string" ? body.detail : undefined;
    } catch {
      // response wasn't JSON; ignore, fall back to generic message
    }
    console.error(
      `API request returned ${response.status}: ${init?.method ?? "GET"} ${path}`
    );
    throw new ApiError(
      detail ?? "Something went wrong on our end. Please try again shortly.",
      { status: response.status }
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  try {
    return (await response.json()) as T;
  } catch (err) {
    console.error(`Failed to parse API response: ${init?.method ?? "GET"} ${path}`, err);
    throw new ApiError("The server sent an unexpected response.", { cause: err });
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: body !== undefined ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
