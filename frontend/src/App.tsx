import { Outlet } from "react-router-dom";
import { NavBar } from "./components/NavBar";

export function App() {
  return (
    <div>
      <a href="#main-content" className="visually-hidden">
        Skip to main content
      </a>
      <NavBar />
      <main id="main-content">
        <Outlet />
      </main>
    </div>
  );
}
