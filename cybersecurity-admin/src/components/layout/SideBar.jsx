import React, { useEffect, useState } from "react";
import { Layout, Menu, Dropdown, Input, message } from "antd";
import {
  DashboardOutlined,
  AppstoreOutlined,
  SecurityScanOutlined,
  DatabaseOutlined,
  PlusOutlined,
  LinkOutlined,
  DownOutlined,
  BranchesOutlined,
  SettingOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { LogoutOutlined } from "@ant-design/icons";
import Logo from "../../assets/images/logo.png";

const { Sider } = Layout;
const { TextArea } = Input;

const Sidebar = ({ collapsed, toggleCollapse, handleLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  return (
    <>
      <Sider
        collapsible
        collapsed={collapsed}
        width={250}
        trigger={null}
        style={{
          background: "#1A4D1A",
          position: "fixed",
          height: "100vh",
          left: 0,
          overflow: "auto",
          boxShadow: "2px 0 5px rgba(0, 0, 0, 0.1)",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "20px",
            paddingBottom: "5px",
            fontSize: "20px",
            fontWeight: "bold",
            color: "#fff",
            textAlign: "center",
            background: "#1A4D1A",
          }}
        >
          {collapsed ? "DCW" : <img src={Logo} alt="DCC CyberWacht Logo" />}
        </div>

        {/* Admin  */}
        <div
          style={{
            textAlign: "center",
            color: "#fff",
            fontSize: "20px",
            fontWeight: "500",
            marginTop: "10px",
            paddingBottom: "0px",
          }}
        >
          Admin
        </div>

        {/* Sidebar Menu */}
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={["/"]}
          selectedKeys={[location.pathname]}
          style={{
            height: "calc(100% - 150px)",
            borderRight: 0,
            backgroundColor: "#1A4D1A",
          }}
        >
          <Menu.Divider
            style={{
              borderBottomColor: "#3D856B",
              borderBottomWidth: "0.1px",
              margin: "18px 15px",
            }}
          />
           <Menu.Item
            key="/"
            icon={<SettingOutlined />}
            onClick={() => navigate("/")}
            style={{
              marginBottom: "-4px",
              color:
                location.pathname === "/" ? "#6BE992" : "inherit",
            }}
          >
            Compliance
          </Menu.Item>
          <Menu.Item
            key="/compliance"
            icon={<BranchesOutlined />}
            onClick={() => navigate("/frameworks")}
            style={{
              marginBottom: "-4px",
              color: location.pathname.startsWith("/frameworks")
                ? "#6BE992"
                : "inherit",
            }}
          >
            Frameworks
          </Menu.Item>
          <Menu.Divider
            style={{
              borderBottomColor: "#3D856B",
              borderWidth: "0.3px",
              margin: "18px 15px",
            }}
          />
          <Menu.Item
            key="/ScanType"
            icon={<SecurityScanOutlined />}
            onClick={() => navigate("/scantype")}
            style={{
              marginBottom: "-4px",
              color: location.pathname === "/scantype" ? "#6BE992" : "inherit",
            }}
          >
            Scan Type
          </Menu.Item>
          <Menu.Item
            key="/ScannersData"
            icon={<DatabaseOutlined />}
            onClick={() => navigate("/ScannersData")}
            style={{
              marginBottom: "-4px",
              color:
                location.pathname === "/ScannersData" ? "#6BE992" : "inherit",
            }}
          >
            Scanners Data
          </Menu.Item>

          <Menu.Item
            key="/vapt-reports"
            icon={<UploadOutlined />}
            onClick={() => navigate("/vapt-reports")}
            style={{
              marginBottom: "-4px",
              color: location.pathname === "/vapt-reports" ? "#6BE992" : "inherit",
            }}
          >
            VAPT Reports
          </Menu.Item>

          <Menu.Divider
            style={{
              borderBottomColor: "#3D856B",
              borderBottomWidth: "0.1px",
              margin: "18px 15px",
            }}
          />
          <Menu.Item
            key="logout"
            icon={<LogoutOutlined />}
            onClick={handleLogout}
            style={{
              position: "absolute",
              bottom: "20px",
              right: "20px",
              color: "#fff",
              padding: "8px 60px",
            }}
          >
            Logout
          </Menu.Item>
        </Menu>
      </Sider>
      ;
    </>
  );
};

export default Sidebar;
