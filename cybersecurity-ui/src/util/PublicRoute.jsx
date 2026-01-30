import { Navigate } from "react-router-dom";

// PublicRoute redirects to home if the user is logged in
const isAuthenticated = () => {
  const token = localStorage.getItem("token");
  return token !== null;
};

const PublicRoute = ({ element }) => {
  return isAuthenticated() ? <Navigate to="/" replace /> : element;
};

export default PublicRoute;
