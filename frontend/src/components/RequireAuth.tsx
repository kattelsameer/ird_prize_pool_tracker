import { Navigate, Outlet } from "react-router-dom";
import { useCurrentUser } from "../api/auth";
import { getStoredToken } from "../api/client";
import { LoadingState } from "./LoadingState";

/**
 * Gates every route under it behind a valid session. No stored token at all
 * skips straight to the login redirect (no point spending a request);
 * a stored token is verified against GET /api/auth/me so an expired/invalid
 * one still bounces to login rather than rendering a broken authenticated
 * page (client.ts's 401 handling already cleared the token by the time
 * `isError` is true here).
 */
export function RequireAuth() {
  const hasToken = Boolean(getStoredToken());
  const me = useCurrentUser();

  if (!hasToken) return <Navigate to="/login" replace />;
  if (me.isLoading) return <LoadingState label="Loading your account…" />;
  if (me.isError) return <Navigate to="/login" replace />;

  return <Outlet />;
}
