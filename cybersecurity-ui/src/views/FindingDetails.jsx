import { Collapse, Typography } from "antd";
import React from "react";

const { Title, Text } = Typography;
const { Panel } = Collapse;

const FindingDetails = () => {
  const findings = {
    "Finding 1": "Details about finding 1...",
    "Finding 2": "Details about finding 2...",
    "Finding 3": "Details about finding 3...",
  };

  const panelStyle = {
    marginBottom: "10px",
    border: "1px solid #e0e0e0",
    borderRadius: "8px",
    overflow: "hidden",
    backgroundColor: "#fafafa",
  };

  return (
    <div style={{ padding: "24px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        Finding Details
      </Title>
      <Collapse
        accordion
        bordered={false}
        defaultActiveKey={["0"]}
        style={{ background: "#fff" }}
      >
        {Object.entries(findings).map(([key, value], index) => (
          <Panel header={key} key={index} style={panelStyle}>
            <Text>{value}</Text>
          </Panel>
        ))}
      </Collapse>
    </div>
  );
};

export default FindingDetails;
