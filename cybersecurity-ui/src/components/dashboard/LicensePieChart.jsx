import React from "react";
import { Typography, Button } from "antd";
import { Pie } from "react-chartjs-2";
import { Chart, ArcElement, Tooltip, Legend } from "chart.js";
import { useNavigate } from "react-router-dom";

const { Title } = Typography;

// Register necessary components for Chart.js
Chart.register(ArcElement, Tooltip, Legend);

const LicensePieChart = ({ data }) => {
  const navigate = useNavigate();

  // Ensure data is correctly formatted
  const chartData = {
    labels: data.map((item) => item.name),
    datasets: [
      {
        data: data.map((item) => item.value),
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
        ], // Add more colors if needed
        borderWidth: 2,
      },
    ],
  };

  // Combine labels, data, and colors into an array of objects
  const combinedData = data.map((item, index) => ({
    label: item.name,
    value: item.value,
    color: chartData.datasets[0].backgroundColor[index],
  }));

  // Sort by value in descending order
  combinedData.sort((a, b) => b.value - a.value);

  // Take the top 4 items for the legend
  const top4Data = combinedData.slice(0, 4);

  // Configuration options for Donut Chart
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "60%", // Creates the donut effect (adjustable percentage)
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          font: {
            size: 12,
          },
          color: "#333",
          // Custom legend filter to show only top 4 items
          filter: (legendItem, chartData) => {
            return top4Data.some((item) => item.label === legendItem.text);
          },
        },
      },
      tooltip: {
        callbacks: {
          label: (tooltipItem) => {
            const value = tooltipItem.raw.toFixed(2);
            return `${tooltipItem.label}: ${value}`;
          },
        },
      },
    },
  };

  return (
    <div
      style={{
        maxWidth: "500px",
        width: "100%",
        margin: "0 auto",
        height: "400px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "2px",
          marginBottom: "20px",
        }}
      >
        <Title level={4} style={{ margin: 0, textAlign: "center" }}>
          License Stats
        </Title>
      </div>

      <Pie data={chartData} options={options} />
    </div>
  );
};

export default LicensePieChart;
