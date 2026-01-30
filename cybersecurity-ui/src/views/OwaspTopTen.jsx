import React from "react";
import { useFetchOwaspTopTenQuery } from "../store/api/cyberService/asvsApi";
import { Typography, Spin } from "antd";
import OwaspFramework from "../components/owaspTopTen/Owasp";

const { Title } = Typography;

function OwaspTopTen() {
  const { data, error, isLoading } = useFetchOwaspTopTenQuery();

  if (isLoading) {
    return (
      <div
        style={{ display: "flex", justifyContent: "center", marginTop: "20px" }}
      >
        <Spin size="large" />
      </div>
    );
  }

  if (!data || !data.data || error) return <div>No data available</div>;

  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        OWASP Top 10 Breakdown
      </Title>
      <OwaspFramework data={data} />
    </div>
  );
}

export default OwaspTopTen;
