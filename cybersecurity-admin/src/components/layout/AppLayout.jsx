import React, { useState } from "react";
import { Avatar, Layout, Menu, theme } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { logout, setSelectedProject } from "../../store/authSlice";
import Sidebar from "./SideBar";
import AppHeader from "./Header";
import {
  AppstoreAddOutlined,
  LogoutOutlined,
  UserOutlined,
} from "@ant-design/icons";

const { Content } = Layout;

const AppLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const user = useSelector((state) => state.auth.user);
  const selectedProject = useSelector((state) => state.auth.selectedProject);
  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();
  const { token } = theme.useToken();

  const handleLogout = () => {
    localStorage.removeItem("token");
    dispatch(logout());
    dispatch(setSelectedProject(null));
    localStorage.removeItem("selectedProject");
    localStorage.removeItem("persist:root");
    navigate("/login");
  };

  const toggleCollapse = () => {
    setCollapsed(!collapsed);
  };

  const formatTitle = (title) =>
    title
      .split(/[-/]/)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

  const breadcrumbItems = location.pathname
    .split("/")
    .filter((item) => item)
    .map((item, index, array) => ({
      title: formatTitle(item),
      path: "/" + array.slice(0, index + 1).join("/"),
    }));

  const getUserInitials = () => {
    if (!user || !user?.name) return "";
    return user.name
      .split(" ")
      .map((part) => part.charAt(0).toUpperCase())
      .join("");
  };

  const menu = (
    <Menu
      style={{
        padding: "10px",
        width: 200,
        borderRadius: "8px",
        boxShadow: "0px 3px 10px rgba(0, 0, 0, 0.1)",
      }}
    >
      <Menu.Item disabled style={{ padding: "5px 0" }}>
        <div
          style={{
            display: "flex",
            borderRadius: "3px",
            alignItems: "center",
            padding: "10px",
            background: "#f2f2f2",
            width: "100%",
          }}
        >
          <Avatar
            style={{
              backgroundColor: "#113032",
              verticalAlign: "middle",
              fontSize: "18px",
              marginRight: "10px",
            }}
            size="large"
          >
            {getUserInitials()}
          </Avatar>
          <div>
            <div
              style={{
                fontWeight: "500",
                fontSize: "14px",
                color: token.colorPrimary,
              }}
            >
              {user?.name}
            </div>
            <div style={{ color: "gray", fontSize: "12px" }}>{user?.email}</div>
          </div>
        </div>
      </Menu.Item>
    </Menu>
  );

  return (
    <Layout style={{ minHeight: "100vh", background: "#f0f2f5" }}>
      <Sidebar
        collapsed={collapsed}
        toggleCollapse={toggleCollapse}
        handleLogout={handleLogout}
      />
      <Layout
        style={{
          marginLeft: collapsed ? 80 : 250,
          transition: "all 0.3s ease",
        }}
      >
        <AppHeader
          collapsed={collapsed}
          toggleCollapse={toggleCollapse}
          breadcrumbItems={breadcrumbItems}
          menu={menu}
          getUserInitials={getUserInitials}
        />
        <Content
          style={{
            padding: 24,
            background: "#fff",
            minHeight: "100vh",
            borderRadius: "8px",
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
