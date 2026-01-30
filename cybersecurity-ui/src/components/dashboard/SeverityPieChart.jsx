// SeverityPieChart.js
import React from "react";
import { Pie } from "@ant-design/plots";
import { Card } from "antd";

const SeverityPieChart = () => {
  const data = [
    { type: "Critical", value: 10 },
    { type: "High", value: 30 },
    { type: "Medium", value: 20 },
    { type: "Low", value: 15 },
    { type: "Informational", value: 25 },
  ];

  const config = {
    appendPadding: 10,
    data,
    angleField: "value",
    colorField: "type",
    radius: 1,
    innerRadius: 0.6, // Creates the "donut" style by leaving space in the center
    label: {
      type: "spider", // Changed label style to "spider" for better readability
      labelHeight: 28,
      content: "{name}\n{percentage}", // Shows the label with percentage
      style: {
        fontSize: 14,
        textAlign: "center",
      },
    },
    statistic: {
      title: false, // Disable default title in the center
      content: {
        style: {
          fontSize: 24,
          fontWeight: "bold",
          fill: "#4D4D4D",
        },
        content: "Severity", // Custom content in the center of the donut
      },
    },
    interactions: [{ type: "element-active" }],
  };

  return (
    <Card title="Historical Finding Severity" style={{ marginBottom: "30px" }}>
      <Pie {...config} />
    </Card>
  );
};

export default SeverityPieChart;
