import { createBrowserRouter, RouterProvider } from "react-router-dom";
import PublicRoute from "./util/PublicRoute";
import ProtectedRoute from "./util/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";
import Login from "./views/Login";
import NotFound from "./views/NotFound";
import ScanType from "./views/ScanType";
import ScannersData from "./views/ScannersData";
import Compliance from "./views/Compliance";
import Frameworks from "./views/Frameworks";
import Samm from "./views/Samm";
import Asvs from "./views/Asvs";
import OwaspTopTen from "./views/OwaspTopTen";
import VaptReportManagement from "./views/VaptReportUpload";
 
const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        path:"/",
        element: <ProtectedRoute element={<Compliance/>} />,
      },
      {
        path:"/scantype",
        element: <ProtectedRoute element={<ScanType />} />,
      },
      {
        path:"/scannersData",
        element: <ProtectedRoute element={<ScannersData />} />,
      },
      {
        path:"/frameworks",
        element: <ProtectedRoute element={<Frameworks />} />,
      },
      {
        path:"/frameworks/samm",
        element: <ProtectedRoute element={<Samm />} />,
      },
      {
        path: "/frameworks/asvs",
        element: <ProtectedRoute element={<Asvs />} />,
      },
      {
        path : "/frameworks/owasp-top-ten",
        element: <ProtectedRoute element={<OwaspTopTen />} />,
      },
      {
        path: "/vapt-reports",
        element: <ProtectedRoute element={<VaptReportManagement />} />,
      },
    ],
    // errorElement: <Error />,
  },
  {
    path: "/login",
    element: <PublicRoute element={<Login />} />,
  },
  {
    path: "*", 
    element: <NotFound />,
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
