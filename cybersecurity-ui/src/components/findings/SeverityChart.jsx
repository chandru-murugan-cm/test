import React, { useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart, ArcElement, Tooltip } from "chart.js";

Chart.register(ArcElement, Tooltip); // Register the Tooltip plugin

// Data for the doughnut chart
const data = {
  datasets: [
    {
      data: [25, 25, 25, 25], // Example data values
      backgroundColor: ["#90EE90", "#FFFF00", "#FFA500", "#FF0000"], // Color for each segment
    },
  ],
  labels: ['Low', 'Medium', 'High', 'Critical'], // Labels corresponding to each color
};

const SeverityChart = ({ totalIssues = 90 }) => {
  const [isTooltipVisible, setIsTooltipVisible] = useState(false);

  // Calculate the rotation angle for the needle
  const needleRotation = (totalIssues / 100) * 180 - 90; // Total issues as a percentage of the full circle (half-circle)

  return (
    <div
      style={{
        position: "relative",
        width: "200px",
        height: "200px",
        borderRadius: "10px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        padding: "50px",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Central overlay content */}
      <div
        style={{
          position: "absolute",
          textAlign: "center",
          marginTop: "120px",
          color: "#000000", // Black text color for visibility
        }}
      >
        <div
          style={{
            fontSize: "24px",
            fontWeight: "bold",
            marginBottom: "5px",
          }}
        >
          {totalIssues}
        </div>
        <div style={{ fontSize: "12px", marginTop: "5px" }}>Total Issues</div>
      </div>

      {/* Doughnut Chart */}
      <Doughnut
        data={data}
        options={{
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              enabled: true,
              position: "nearest",
              callbacks: {
                label: (tooltipItem) => {
                  const value = tooltipItem.raw;
                  const label = tooltipItem.label;
                  return `${label}: ${value}%`;
                },
                title: () => '',
              },
              // Event listeners for tooltip visibility
              external: (tooltipModel) => {
                setIsTooltipVisible(tooltipModel.opacity > 0);
              },
            },
          },
          rotation: -90,
          circumference: 180,
          cutout: "80%",
          maintainAspectRatio: true,
          responsive: true,
        }}
      />

      {/* Needle */}
      {!isTooltipVisible && (
        <div
          style={{
            position: "absolute",
            width: "2px",
            height: "35px",
            backgroundColor: "#FF0000",
            top: "90px",
            left: "50%",
            transformOrigin: "bottom",
            transform: `rotate(${needleRotation}deg)`,
            zIndex: 100,
          }}
        ></div>
      )}
    </div>
  );
};

export default SeverityChart;
