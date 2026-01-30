import React from "react";
import { Card, Typography, Avatar, Space, Divider, Row, Col } from "antd";
import { useSelector } from "react-redux";
import { FaCircleUser } from "react-icons/fa6";
import { MdEmail } from "react-icons/md";

const { Title, Text } = Typography;

const cardStyle = {
  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
  borderRadius: "8px",
  padding: "8px",
  marginBottom: "20px",
  width: "100%",
};

function ProfilePage() {
  // Fetch user data from Redux store
  const user = useSelector((state) => state.auth.user);

  return (
    <div
      style={{
        padding: "20px",
        minHeight: "100vh",
        margin: 0,
      }}
    >
      {/* Header Section */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center" }}>
          <Avatar
            size={80}
            style={{
              backgroundColor: "#113032",
              color: "#fff",
              fontSize: "36px",
            }}
          >
            {user?.name
              ? user.name
                  .split(" ")
                  .map((part) => part[0])
                  .join("")
                  .toUpperCase()
              : "N/A"}
          </Avatar>
          <div style={{ marginLeft: "16px" }}>
            <Title level={4} style={{ margin: 0 }}>
              {user?.name || "Guest User"}
            </Title>
            <Text>My Profile</Text>
          </div>
        </div>
        <div>
          <Space>
            <Text style={{ color: "#8c8c8c", cursor: "pointer" }}>Docs</Text>
          </Space>
        </div>
      </div>

      {/* Content Section */}
      <Row gutter={24}>
        {/* Left Card: Personal Profile */}
        <Col span={12}>
          <Card title="Personal Profile" bordered={false} style={cardStyle}>
            <Space size="middle">
              <FaCircleUser
                style={{ fontSize: "20px", color: "#6BE992", marginTop: "4px" }}
              />
              <Text>{user?.name} </Text>
            </Space>
            <Divider />
            <Space size="middle">
              <MdEmail
                style={{ fontSize: "20px", color: "#6BE992", marginTop: "4px" }}
              />
              <Text>{user?.email || "No email available"} </Text>
            </Space>
          </Card>
        </Col>

        {/* Right Card: Email Notifications */}
      </Row>
    </div>
  );
}

export default ProfilePage;
