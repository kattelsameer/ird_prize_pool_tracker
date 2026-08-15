import { NavLink } from "react-router-dom";
import { NotificationBell } from "./NotificationBell";
import styles from "./NavBar.module.css";

const LINKS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/coupons", label: "My Coupons" },
  { to: "/prize-pool", label: "Prize Pool Explorer" },
  { to: "/settings", label: "Settings" },
  { to: "/information", label: "About the Program" },
];

export function NavBar() {
  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <span aria-hidden="true">🎟</span> CouponSathi
      </div>
      <nav className={styles.nav} aria-label="Main navigation">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ""}`}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div className={styles.actions}>
        <NotificationBell />
      </div>
    </header>
  );
}
