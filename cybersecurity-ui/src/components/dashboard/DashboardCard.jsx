import React from "react";
import { Col, Typography } from "antd";

const { Title } = Typography;

const DashboardCard = ({ icon, title, value, color }) => {
  return (
    <Col xs={24} sm={12} md={6}>
      <div
        style={{
          background: "#ffffff",
          borderRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          padding: "16px",
          display: "flex",
          justifyContent: "flex-start",
          gap: "25px",
          alignItems: "center",
          height: "120px",
        }}
      >
        {icon}
        <div>
          <Title
            level={5}
            style={{
              margin: 0,
              fontSize: "14px",
              marginBottom: "4px",
            }}
          >
            {title}
          </Title>
          <p
            style={{
              fontSize: "14px",
              color: "#8c8c8c",
              margin: 0,
            }}
          >
            {value} Issues
          </p>
        </div>
      </div>
    </Col>
  );
};

export default DashboardCard;
