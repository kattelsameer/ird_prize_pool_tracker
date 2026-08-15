import { ApiError } from "../api/client";
import styles from "./ErrorState.module.css";

export interface ErrorStateProps {
  error: unknown;
  /** Fallback user-safe message if the error isn't an ApiError. */
  fallbackMessage?: string;
  onRetry?: () => void;
}

export function ErrorState({
  error,
  fallbackMessage = "Something went wrong. Please try again.",
  onRetry,
}: ErrorStateProps) {
  const message = error instanceof ApiError ? error.message : fallbackMessage;

  return (
    <div className={styles.wrapper} role="alert">
      <span aria-hidden="true" className={styles.icon}>
        ⚠
      </span>
      <p className={styles.message}>{message}</p>
      {onRetry && (
        <button type="button" onClick={onRetry} className={styles.retryButton}>
          Try again
        </button>
      )}
    </div>
  );
}
