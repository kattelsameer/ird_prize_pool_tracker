import { useId, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLogin } from "../api/auth";
import { ErrorState } from "../components/ErrorState";
import styles from "./AuthForm.module.css";

export function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useLogin();
  const navigate = useNavigate();
  const formId = useId();

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    login.mutate(
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
        <p className={styles.subtitle}>Log in to track your coupons</p>

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
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {login.isError && (
          <ErrorState error={login.error} fallbackMessage="Incorrect email or password." />
        )}

        <button type="submit" className={styles.submitButton} disabled={login.isPending}>
          {login.isPending ? "Logging in…" : "Log in"}
        </button>

        <p className={styles.switchLink}>
          Don't have an account? <Link to="/register">Create one</Link>
        </p>
      </form>
    </div>
  );
}
