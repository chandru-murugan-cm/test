import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Error from "./views/Error";
import Login from "./views/Login";
import Register from "./views/Register";
import ProtectedRoute from "./util/ProtectedRoute";
import PublicRoute from "./util/PublicRoute";
import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./views/Dashboard";
import Scans from "./views/Scans";
import Findings from "./views/Findings";
import AddProject from "./views/AddProject";
import Projects from "./views/Projects";
import ProjectDetails from "./views/ProjectDetails";
import FindingDetails from "./views/FindingDetails";
import ScansByScanner from "./views/ScansByScanner";
import OAuthCallback from "./views/OAuthCallback";
import GitLabOAuthCallback from "./views/GitLabOAuthCallback";
import LicenceSbom from "./views/LicenceSbom";
import LanguageFramework from "./views/LanguageFramework";
import Profile from "./views/Profile";
import NotFound from "./views/NotFound";
import Domain from "./views/Domain";
import Contract from "./views/Contract";
import Repositories from "./views/Repositories";
import Compliance from "./views/compliance";
import ComplianceDetails from "./views/ComplianceDetails";
import ForgotPassword from "./views/ForgotPassword";
import ResetPassword from "./views/ResetPassword";
import Samm from "./views/Samm";
import Cloud from "./views/Cloud";
import Frameworks from "./views/Frameworks";
import Asvs from "./views/Asvs";
import OwaspTopTen from "./views/OwaspTopTen";
import VaptReports from "./views/VaptReports";
import UserVaptReports from "./views/UserVaptReports";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        path: "/",
        element: <ProtectedRoute element={<Dashboard />} />,
      },
      {
        path: "/new-project",
        element: <ProtectedRoute element={<AddProject />} />,
      },

      {
        path: "/scans",
        element: <ProtectedRoute element={<Scans />} />,
      },
      {
        path: "/license",
        element: <ProtectedRoute element={<LicenceSbom />} />,
      },
      {
        path: "/languages",
        element: <ProtectedRoute element={<LanguageFramework />} />,
      },
      {
        path: "/scans/:id",
        element: <ProtectedRoute element={<Findings />} />,
      },
      {
        path: "/scans/:id/finding/:findingId",
        element: <ProtectedRoute element={<FindingDetails />} />,
      },
      {
        path: "/findings",
        element: <ProtectedRoute element={<Findings />} />,
      },
      {
        path: "/compliance",
        element: <ProtectedRoute element={<Compliance />} />,
      },
      {
        path: "/complianceDetails",
        element: <ProtectedRoute element={<ComplianceDetails />} />,
      },
      {
        path: "/domains",
        element: <ProtectedRoute element={<Domain />} />,
      },
      {
        path: "/contracts",
        element: <ProtectedRoute element={<Contract />} />,
      },
      {
        path: "/cloud",
        element: <ProtectedRoute element={<Cloud />} />,
      },
      {
        path: "/repositories",
        element: <ProtectedRoute element={<Repositories />} />,
      },
      {
        path: "/findings/:findingId",
        element: <ProtectedRoute element={<FindingDetails />} />,
      },
      {
        path: "/projects",
        element: <ProtectedRoute element={<Projects />} />,
      },
      {
        path: "/project",
        element: <ProtectedRoute element={<ProjectDetails />} />,
      },
      {
        path: "/scans/:scannerId",
        element: <ProtectedRoute element={<ScansByScanner />} />,
      },
      {
        path: "/projects/:id/scanner/:scannerId/scan/:scanId",
        element: <ProtectedRoute element={<Findings />} />,
      },
      {
        path: "/projects/:id/scanner/:scannerId/scan/:scanId/finding/:findingId",
        element: <ProtectedRoute element={<FindingDetails />} />,
      },
      {
        path: "/profile",
        element: <ProtectedRoute element={<Profile />} />,
      },
      {
        path: "/frameworks",
        element: <ProtectedRoute element={<Frameworks />} />,
      },
      {
        path: "/frameworks/samm",
        element: <ProtectedRoute element={<Samm />} />,
      },
      {
        path: "/frameworks/asvs",
        element: <ProtectedRoute element={<Asvs />} />,
      },
      {
        path: "/frameworks/owasp-top-ten",
        element: <ProtectedRoute element={<OwaspTopTen />} />,
      },
      {
        path: "/projects/:projectId/vapt-reports",
        element: <ProtectedRoute element={<VaptReports />} />,
      },
      {
        path: "/vapt-reports",
        element: <ProtectedRoute element={<UserVaptReports />} />,
      },
    ],
    errorElement: <Error />,
  },
  {
    path: "/login",
    element: <PublicRoute element={<Login />} />,
  },
  {
    path: "/register",
    element: <PublicRoute element={<Register />} />,
  },

  {
    path: "/oauth-callback",
    element: <ProtectedRoute element={<OAuthCallback />} />,
  },
  {
    path: "/gitlab-oauth-callback",
    element: <ProtectedRoute element={<GitLabOAuthCallback />} />,
  },
  {
    path: "/forgot-password",
    element: <PublicRoute element={<ForgotPassword />} />,
  },
  {
    path: "/reset-password/:token",
    element: <PublicRoute element={<ResetPassword />} />,
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
