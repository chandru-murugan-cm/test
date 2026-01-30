import React from "react";
import {
  Layout,
  Button,
  Avatar,
  Dropdown,
  Space,
  Typography,
  Input,
} from "antd";
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SettingOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";

const { Header } = Layout;
const { Title, Text } = Typography;

const AppHeader = ({
  collapsed,
  toggleCollapse,
  breadcrumbItems,
  menu,
  getUserInitials,
}) => {
  const navigate = useNavigate();
  const user = useSelector((state) => state.auth.user);

  return (
    <Header
      style={{
        padding: "0 20px",
        background: "#fff",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        boxShadow: "0px 1px 5px rgba(0, 0, 0, 0.1)",
        position: "sticky",
        top: 0,
        zIndex: 1,
      }}
    >
      <div style={{ display: "flex", alignItems: "center" }}>
        <Button
          type="text"
          onClick={toggleCollapse}
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          style={{ fontSize: "18px", transition: "all 0.3s ease" }}
        />

        <Title
          level={5}
          style={{ margin: 0, marginLeft: "8px", fontWeight: "500" }}
        >
          Hi Admin
        </Title>
      </div>
    </Header>
  );
};

export default AppHeader;
