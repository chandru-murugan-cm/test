import React from "react";
import { Table, Spin, Alert } from "antd";
import { PieChartOutlined } from "@ant-design/icons";
import { useFetchLanguagesAndFrameworkByProjectIdQuery } from "../../store/api/cyberService/repoScanResultsApi.js";

function LanguageOverview({ project_id }) {
  const {
    data: languagesData,
    error,
    isLoading,
  } = useFetchLanguagesAndFrameworkByProjectIdQuery(project_id);
  
  // Handle loading state
  if (isLoading) return <Spin size="large" />;

  // Handle error state
  if (error)
    return (
      <Alert message="Error" description="Error fetching data" type="error" />
    );

  // Check if data exists and is an array
  const languages = languagesData?.data || [];

  // Columns for the Ant Design Table
  const columns = [
    {
      title: "Language Name",
      dataIndex: "language_name",
      key: "language_name",
      render: (languageName) => (
        <span>
          <PieChartOutlined style={{ marginRight: "8px", color: "#1890ff" }} />
          {languageName}
        </span>
      ),
    },
    {
      title: "Language Count",
      dataIndex: "language_count",
      key: "language_count",
    },
    {
      title: "Language Percentage",
      dataIndex: "language_percentage",
      key: "language_percentage",
      render: (percentage) => `${percentage}%`,
    },
  ];

  return (
    <div style={{ marginTop: "10px" }}>
      <Table
        columns={columns}
        dataSource={languages}
        rowKey={(record) => record.language_name}
        bordered
      />
    </div>
  );
}

export default LanguageOverview;
