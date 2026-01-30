import React from "react";
import { Typography } from "antd";
import { useSelector } from "react-redux";
import LanguageOverview from "../components/languageFrameworks/LanguageOverview";

const { Title } = Typography;

function LanguageFramework() {
  const selectedProject = useSelector((state) => state.auth.selectedProject);
  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        Language & Framework
      </Title>
      <LanguageOverview project_id={selectedProject?._id} />
    </div>
  );
}

export default LanguageFramework;
