// ScanCard.js
import React from "react";
import { Card, Typography } from "antd";

const { Title } = Typography;

const ScanCard = ({ title, value, icon }) => {
  return (
    <Card
      hoverable
      style={{
        borderRadius: "10px",
        backgroundColor: "#fff",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
        transition: "all 0.3s ease",
      }}
      bodyStyle={{ padding: "24px" }}
    >
      <div style={{ display: "flex", alignItems: "center" }}>
        <div style={{ marginRight: "16px" }}>{icon}</div>
        <div>
          <Title level={4} style={{ margin: 0 }}>
            {value}
          </Title>
          <span style={{ color: "#888" }}>{title}</span>
        </div>
      </div>
    </Card>
  );
};

export default ScanCard;
