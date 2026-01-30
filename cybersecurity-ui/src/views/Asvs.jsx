import { Typography } from "antd";
import React from "react";
import Chapter from "../components/asvs/Chapter";

const { Title } = Typography;

function Asvs() {
  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        ASVS (Application Security Verification Standard)
      </Title>
      <Chapter />
    </div>
  );
}

export default Asvs;
