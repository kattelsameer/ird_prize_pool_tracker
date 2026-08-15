import { useId, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useRegister } from "../api/auth";
import { ErrorState } from "../components/ErrorState";
import styles from "./AuthForm.module.css";

const MIN_PASSWORD_LENGTH = 8;

export function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [touched, setTouched] = useState(false);
  const register = useRegister();
  const navigate = useNavigate();
  const formId = useId();

  const passwordError =
    touched && password.length > 0 && password.length < MIN_PASSWORD_LENGTH
      ? `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`
      : null;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setTouched(true);
    if (password.length < MIN_PASSWORD_LENGTH) return;
    register.mutate(
      { email, password },
      { onSuccess: () => navigate("/", { replace: true }) }
    );
  }

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit} noValidate>
        <h1 className={styles.title}>
          <span aria-hidden="true">🎟</span> CouponSathi
        </h1>
        <p className={styles.subtitle}>Create an account to start tracking your coupons</p>

        <div className={styles.field}>
          <label htmlFor={`${formId}-email`}>Email</label>
          <input
            id={`${formId}-email`}
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className={styles.field}>
          <label htmlFor={`${formId}-password`}>Password</label>
          <input
            id={`${formId}-password`}
            type="password"
            autoComplete="new-password"
            required
            minLength={MIN_PASSWORD_LENGTH}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-invalid={Boolean(passwordError)}
            aria-describedby={passwordError ? `${formId}-password-error` : `${formId}-password-hint`}
          />
          <p id={`${formId}-password-hint`} className={styles.hint}>
            At least {MIN_PASSWORD_LENGTH} characters.
          </p>
          {passwordError && (
            <p id={`${formId}-password-error`} className={styles.error}>
              {passwordError}
            </p>
          )}
        </div>

        {register.isError && (
          <ErrorState
            error={register.error}
            fallbackMessage="We couldn't create your account. Please try again."
          />
        )}

        <button type="submit" className={styles.submitButton} disabled={register.isPending}>
          {register.isPending ? "Creating account…" : "Create account"}
        </button>

        <p className={styles.switchLink}>
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}
