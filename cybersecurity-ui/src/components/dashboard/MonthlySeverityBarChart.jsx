// MonthlySeverityBarChart.js
import React from "react";
import { Column } from "@ant-design/plots";
import { Card } from "antd";

const MonthlySeverityBarChart = () => {
  const data = [
    { month: "Jan", severity: "High", count: 4 },
    { month: "Jan", severity: "Medium", count: 2 },
    { month: "Jan", severity: "Low", count: 1 },
    { month: "Jan", severity: "Informational", count: 5 },
    { month: "Feb", severity: "High", count: 3 },
    { month: "Feb", severity: "Medium", count: 5 },
    { month: "Feb", severity: "Low", count: 2 },
    { month: "Feb", severity: "Informational", count: 3 },
    { month: "Mar", severity: "High", count: 2 },
    { month: "Mar", severity: "Medium", count: 3 },
    { month: "Mar", severity: "Low", count: 4 },
    { month: "Mar", severity: "Informational", count: 6 },
    { month: "Apr", severity: "High", count: 5 },
    { month: "Apr", severity: "Medium", count: 2 },
    { month: "Apr", severity: "Low", count: 3 },
    { month: "Apr", severity: "Informational", count: 2 },
    { month: "May", severity: "High", count: 3 },
    { month: "May", severity: "Medium", count: 1 },
    { month: "May", severity: "Low", count: 2 },
    { month: "May", severity: "Informational", count: 5 },
    { month: "Jun", severity: "High", count: 4 },
    { month: "Jun", severity: "Medium", count: 4 },
    { month: "Jun", severity: "Low", count: 3 },
    { month: "Jun", severity: "Informational", count: 1 },
  ];

  const config = {
    data,
    isGroup: true,
    xField: "month",
    yField: "count",
    seriesField: "severity",
    color: ["#ff0000", "#ff9900", "#66cc00", "#00ccff"],
    label: {
      position: "middle",
      style: {
        fill: "#fff",
        opacity: 0.6,
      },
    },
    interactions: [
      {
        type: "active-region",
        enable: false,
      },
    ],
  };

  return (
    <Card
      title="Reported Finding Severity by Month"
      style={{ marginBottom: "30px" }}
    >
      <Column {...config} />
    </Card>
  );
};

export default MonthlySeverityBarChart;
