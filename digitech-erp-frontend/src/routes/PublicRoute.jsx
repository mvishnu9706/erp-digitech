import { Navigate, Outlet } from "react-router-dom";

const PublicRoute = () => {

    const isAuthenticated = Boolean(localStorage.getItem("token"));

    return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Outlet />;

};

export default PublicRoute;