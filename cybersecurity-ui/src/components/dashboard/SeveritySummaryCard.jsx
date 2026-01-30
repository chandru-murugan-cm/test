import React from "react";
import { Col } from "antd";
import { BsFillPieChartFill } from "react-icons/bs";

const SeveritySummaryCard = ({ findingSummary }) => {
  return (
    <Col xs={24} sm={12} md={6}>
      <div
        style={{
          background: "#ffffff",
          borderRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          padding: "10px",
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "flex-start",
          gap: "25px",
          height: "120px",
        }}
      >
        <BsFillPieChartFill size={50} color="#6BE992" />

        <div
          style={{
            fontSize: "14px",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            gap: "4px",
          }}
        >
          {/* First Row - Critical & High */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: "10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  backgroundColor: "#ff4d4f",
                  display: "inline-block",
                }}
              ></span>
              <span style={{ fontSize: "14px" }}>
                Critical: {findingSummary?.severity_counts?.critical}
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  backgroundColor: "#ffcc00",
                  display: "inline-block",
                }}
              ></span>
              <span style={{ fontSize: "14px" }}>
                High: {findingSummary?.severity_counts?.high}
              </span>
            </div>
          </div>

          {/* Second Row - Medium & Low */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: "10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  backgroundColor: "#ffbf00",
                  display: "inline-block",
                }}
              ></span>
              <span style={{ fontSize: "14px" }}>
                Medium: {findingSummary?.severity_counts?.medium}
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  backgroundColor: "#52c41a",
                  display: "inline-block",
                }}
              ></span>
              <span style={{ fontSize: "14px" }}>
                Low: {findingSummary?.severity_counts?.low}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Col>
  );
};

export default SeveritySummaryCard;
