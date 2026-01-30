import React from "react";
import { Typography } from "antd";
import { useState } from "react";
import TabbedView from "../components/samm/HierarchicalTree ";

const { Title } = Typography;

function Samm() {
  const [averageScore, setAverageScore] = useState(null);
  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        SAMM (Software Assurance Maturity Model)
        {averageScore !== null && ` - Score: ${averageScore}`}
      </Title>

      <TabbedView onAverageScoreCalculated={setAverageScore} />
    </div>
  );
}

export default Samm;
