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
  const docs_url = import.meta.env.VITE_DOCS;
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
          Hi {user?.name}
        </Title>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {/* Docs Link */}

        {/* Search Input with Icon Inside */}
        <Input
          placeholder="Search"
          prefix={<SearchOutlined style={{ color: "gray" }} />}
          style={{
            width: 200,
            marginRight: "16px",
          }}
          disabled
        />

        {/* Settings Icon */}
        {/* <SettingOutlined
          style={{
            fontSize: "20px",
            marginRight: "22px",
            cursor: "pointer",
          }}
          onClick={() => navigate(`/project`)}
        /> */}

        {/* Docs Link */}
        <a
          href={"http://127.0.0.1:4000"}  
          target="_blank"   
          rel="noopener noreferrer"
          style={{
            marginRight: "16px",
            cursor: "pointer",
            color: "gray",
            fontSize: "15px",
            textDecoration: "none",
          }}
        >
          Docs
        </a>

        {/* Avatar Dropdown */}
        <Dropdown overlay={menu} trigger={["click"]}>
          <Space>
            <Avatar
              style={{
                backgroundColor: "#113032",
                cursor: "pointer",
              }}
              size="large"
            >
              {getUserInitials()}
            </Avatar>
          </Space>
        </Dropdown>
      </div>
    </Header>
  );
};

export default AppHeader;
