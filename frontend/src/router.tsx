import { createBrowserRouter } from "react-router-dom";
import { App } from "./App";
import { RequireAuth } from "./components/RequireAuth";
import { Dashboard } from "./pages/Dashboard";
import { Coupons } from "./pages/Coupons";
import { CouponDetail } from "./pages/CouponDetail";
import { PrizePoolExplorer } from "./pages/PrizePoolExplorer";
import { Settings } from "./pages/Settings";
import { Information } from "./pages/Information";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";

export const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  {
    element: <RequireAuth />,
    children: [
      {
        path: "/",
        element: <App />,
        children: [
          { index: true, element: <Dashboard /> },
          { path: "coupons", element: <Coupons /> },
          { path: "coupons/:id", element: <CouponDetail /> },
          { path: "prize-pool", element: <PrizePoolExplorer /> },
          { path: "settings", element: <Settings /> },
          { path: "information", element: <Information /> },
        ],
      },
    ],
  },
]);
