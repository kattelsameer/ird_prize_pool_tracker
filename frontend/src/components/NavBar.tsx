import { useEffect, useRef, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useCurrentUser, useLogout } from "../api/auth";
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
  const [menuOpen, setMenuOpen] = useState(false);
  const headerRef = useRef<HTMLElement>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const currentUser = useCurrentUser();
  const logout = useLogout();
  const navId = "primary-navigation";

  // Close the mobile menu on route change -- an in-render state adjustment
  // (React's recommended alternative to a `useEffect` keyed on a changing
  // prop/value: https://react.dev/learn/you-might-not-need-an-effect),
  // not an effect, so it can never cause an extra cascading render commit.
  const [lastPathname, setLastPathname] = useState(location.pathname);
  if (location.pathname !== lastPathname) {
    setLastPathname(location.pathname);
    setMenuOpen(false);
  }

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (headerRef.current && !headerRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setMenuOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  return (
    <header className={styles.header} ref={headerRef}>
      <div className={styles.topRow}>
        <div className={styles.brand}>
          <span aria-hidden="true">🎟</span> CouponSathi
        </div>
        <div className={styles.actions}>
          <NotificationBell />
          <button
            type="button"
            className={styles.menuButton}
            aria-expanded={menuOpen}
            aria-controls={navId}
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span aria-hidden="true">{menuOpen ? "✕" : "☰"}</span>
          </button>
        </div>
      </div>
      <nav
        id={navId}
        className={`${styles.nav} ${menuOpen ? styles.navOpen : ""}`}
        aria-label="Main navigation"
      >
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
        <div className={styles.accountRow}>
          {currentUser.data && <span className={styles.accountEmail}>{currentUser.data.email}</span>}
          <button type="button" className={styles.logoutButton} onClick={handleLogout}>
            Log out
          </button>
        </div>
      </nav>
    </header>
  );
}
