import React from "react";
import ScansByScanner from "../components/scans/ScanByScanner";
import Scans from "../components/projects/Scans";
import { Typography } from "antd";

const { Title } = Typography;

const ScansPage = () => {
  // Define table columns
  const allScans = [
    {
      key: "1",
      scanId: 1,
      projectName: "Project A",
      status: "Success",
      time: "2024-10-10",
      high: 5,
      medium: 3,
      low: 2,
      totalFindings: 10,
    },
    {
      key: "2",
      scanId: 2,
      projectName: "Project B",
      status: "Failed",
      time: "2024-10-09",
      high: 1,
      medium: 2,
      low: 2,
      totalFindings: 5,
    },
    {
      key: "3",
      scanId: 3,
      projectName: "Project C",
      status: "In Progress",
      time: "2024-10-08",
      high: 0,
      medium: 0,
      low: 0,
      totalFindings: 0,
    },
  ];

  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        Scans
      </Title>
      <Scans />
    </div>
  );
};

export default ScansPage;
