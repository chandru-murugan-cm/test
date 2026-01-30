import { Navigate } from "react-router-dom";
const isAuthenticated = () => {
  const token = localStorage.getItem("token");
  return token !== null;
};

const PublicRoute = ({ element }) => {
  return isAuthenticated() ? <Navigate to="/" replace /> : element;
};

export default PublicRoute;
