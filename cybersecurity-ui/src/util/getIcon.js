import {
  LockOutlined,
  FileSearchOutlined,
  CodeOutlined,
  GlobalOutlined,
  ClusterOutlined,
} from "@ant-design/icons";

export const getScanTypeIcon = (scanType) => {
  const iconMap = {
    "Secrets Detection": (
      <LockOutlined style={{ fontSize: "20px", color: "#007BFF" }} />
    ),
    "Licenses and SBOM": (
      <FileSearchOutlined style={{ fontSize: "20px", color: "#28A745" }} />
    ),
    "Dependency Vulnerability Scanner": (
      <CodeOutlined style={{ fontSize: "20px", color: "#FFC107" }} />
    ),
    "Languages and Framework": (
      <CodeOutlined style={{ fontSize: "20px", color: "#6F42C1" }} />
    ),
    "Smart Contract Vulnerability Scanner": (
      <ClusterOutlined style={{ fontSize: "20px", color: "#DDA0DD" }} />
    ),
  };

  return (
    iconMap[scanType] || (
      <GlobalOutlined style={{ fontSize: "20px", color: "#6C757D" }} />
    )
  );
};
