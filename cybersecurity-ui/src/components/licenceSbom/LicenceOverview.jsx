import React, { useState } from "react";
import { useFetchLicensesAndSbomQuery } from "../../store/api/cyberService/repoScanResultsApi.js";
import {
  Table,
  Spin,
  Alert,
  Tag,
  Card,
  Statistic,
  Row,
  Col,
  Tooltip,
  Modal,
  Descriptions,
} from "antd";
import {
  WarningOutlined,
  CheckCircleOutlined,
  EuroCircleFilled,
  InfoCircleOutlined,
  ExclamationCircleOutlined,
  FileTextOutlined,
} from "@ant-design/icons";

function LicenceOverview({ project_id }) {
  const {
    data: licensesAndSbomData,
    error,
    isLoading,
  } = useFetchLicensesAndSbomQuery(project_id);

  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);

  // Handle loading state
  if (isLoading) return <Spin size="large" />;

  // Handle error state
  if (error)
    return (
      <Alert message="Error" description="Error fetching data" type="error" />
    );

  // Check if data exists and is an array
  const licenses = licensesAndSbomData?.data?.findings || [];
  // Function to return icon based on risk level
  const getRiskLevelIcon = (riskLevel) => {
    switch (riskLevel) {
      case "High":
        return <EuroCircleFilled style={{ color: "red" }} />;
      case "Medium":
        return <WarningOutlined style={{ color: "orange" }} />;
      case "Low":
        return <CheckCircleOutlined style={{ color: "green" }} />;
      default:
        return null;
    }
  };

  // Unique values for filtering options
  const uniqueValues = (data, key) => {
    return [...new Set(data.map((item) => item[key]))].map((value) => ({
      text: value,
      value: value,
    }));
  };

  // Columns for the Ant Design Table with filters
  const columns = [
    {
      title: "Package Name",
      dataIndex: "pkg_name",
      key: "pkg_name",
      filters: uniqueValues(licenses, "pkg_name"), // Add filters
      onFilter: (value, record) => record.pkg_name.includes(value),
      render: (text) => (text ? text : "N/A"), // Handle empty package names
    },
    {
      title: "License Name",
      dataIndex: "name",
      key: "name",
      filters: uniqueValues(licenses, "name"), // Add filters
      onFilter: (value, record) => record.name.includes(value),
      sorter: (a, b) => a.name.localeCompare(b.name), // Add sorter for alphabetical order
      defaultSortOrder: "ascend",
      render: (text) => <Tag color="blue">{text}</Tag>, // Use Tag for better visualization
    },
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      filters: uniqueValues(licenses, "severity"), // Add filters
      onFilter: (value, record) => record.severity === value,
      render: (severity) => {
        let color = "";
        switch (severity) {
          case "HIGH":
            color = "red";
            break;
          case "MEDIUM":
            color = "orange";
            break;
          case "LOW":
            color = "green";
            break;
          case "UNKNOWN":
            color = "gray";
            break;
          default:
            color = "black";
        }
        return <Tag color={color}>{severity}</Tag>; // Use Tag for severity levels
      },
    },
    {
      title: "Details",
      key: "details",
      render: (_, record) => (
        <Tooltip title="View Details">
          <InfoCircleOutlined
            style={{ cursor: "pointer", color: "#1890ff" }}
            onClick={() => showDetails(record)}
          />
        </Tooltip>
      ),
    },
  ];

  // Function to show details in a modal
  const showDetails = (record) => {
    setSelectedRecord(record);
    setIsModalVisible(true);
  };

  // Function to close the modal
  const handleCloseModal = () => {
    setIsModalVisible(false);
    setSelectedRecord(null);
  };

  // Expandable row for additional details
  const expandableRow = {
    expandedRowRender: (record) => (
      <div style={{ margin: 0 }}>
        <p>
          <strong>File Path:</strong> {record.file_path || "N/A"}
        </p>
        <p>
          <strong>License Link:</strong>{" "}
          {record.link ? (
            <a href={record.link} target="_blank" rel="noopener noreferrer">
              {record.link}
            </a>
          ) : (
            "N/A"
          )}
        </p>
        <p>
          <strong>License Text:</strong> {record.text || "N/A"}
        </p>
      </div>
    ),
    rowExpandable: (record) => record.file_path || record.link || record.text,
  };

  // Summary statistics
  const summaryStats = licensesAndSbomData?.data?.summary_stats || {};
  const severityStats = licensesAndSbomData?.data?.severity_stats || {};

  return (
    <div style={{ marginTop: "10px" }}>
      {/* Summary Cards */}
<Row gutter={[16, 24]} style={{ marginBottom: "24px" }}>
  {/* Total Licenses Card */}
  <Col span={6}>
    <Card
      hoverable
      style={{
        borderRadius: "12px", // Larger border radius for smoother corners
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)", // Enhanced shadow for better elevation
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        transition: "transform 0.3s ease", // Smooth hover effect
      }}
      bodyStyle={{
        padding: "24px", // Increased padding for more space around the content
      }}
      onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")} // Slight zoom-in effect on hover
      onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
    >
      <FileTextOutlined
        style={{ fontSize: "52px", color: "#1890ff", marginBottom: "16px" }} // Bigger and bolder icon
      />
      <Statistic
        title={
          <span style={{ color: "#595959", fontWeight: "600", fontSize: "16px" }}>Total Packages</span> // Bold and larger text
        }
        value={summaryStats.license_count || 0}
        valueStyle={{ color: "#1890ff", fontSize: "28px", fontWeight: "700" }} // Larger value size
      />
    </Card>
  </Col>

  {/* High Severity Card */}
  <Col span={6}>
    <Card
      hoverable
      style={{
        borderRadius: "12px",
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        transition: "transform 0.3s ease",
      }}
      bodyStyle={{
        padding: "24px",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")}
      onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
    >
      <WarningOutlined
        style={{ fontSize: "52px", color: "#ff4d4f", marginBottom: "16px" }} // Bigger icon with bold color
      />
      <Statistic
        title={
          <span style={{ color: "#595959", fontWeight: "600", fontSize: "16px" }}>High Severity</span>
        }
        value={severityStats.HIGH || 0}
        valueStyle={{ color: "#ff4d4f", fontSize: "28px", fontWeight: "700" }}
      />
    </Card>
  </Col>

  {/* Medium Severity Card */}
  <Col span={6}>
    <Card
      hoverable
      style={{
        borderRadius: "12px",
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        transition: "transform 0.3s ease",
      }}
      bodyStyle={{
        padding: "24px",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")}
      onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
    >
      <ExclamationCircleOutlined
        style={{ fontSize: "52px", color: "#faad14", marginBottom: "16px" }} // Bigger icon with bold color
      />
      <Statistic
        title={
          <span style={{ color: "#595959", fontWeight: "600", fontSize: "16px" }}>Medium Severity</span>
        }
        value={severityStats.MEDIUM || 0}
        valueStyle={{ color: "#faad14", fontSize: "28px", fontWeight: "700" }}
      />
    </Card>
  </Col>

  {/* Low Severity Card */}
  <Col span={6}>
    <Card
      hoverable
      style={{
        borderRadius: "12px",
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        transition: "transform 0.3s ease",
      }}
      bodyStyle={{
        padding: "24px",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")}
      onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
    >
      <CheckCircleOutlined
        style={{ fontSize: "52px", color: "#52c41a", marginBottom: "16px" }} // Bigger icon with bold color
      />
      <Statistic
        title={
          <span style={{ color: "#595959", fontWeight: "600", fontSize: "16px" }}>Low Severity</span>
        }
        value={severityStats.LOW || 0}
        valueStyle={{ color: "#52c41a", fontSize: "28px", fontWeight: "700" }}
      />
    </Card>
  </Col>
</Row>


      {/* Licenses Table */}
      <Table
        columns={columns}
        dataSource={licenses}
        rowKey={(record) => record._id} // Use unique _id as row key
        bordered
        // expandable={expandableRow} // Add expandable rows
        pagination={{ pageSize: 10 }} // Add pagination
      />

      {/* Modal for Viewing Details */}
      <Modal
        title="Package Details"
        visible={isModalVisible}
        onCancel={handleCloseModal}
        footer={null}
      >
        {selectedRecord && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Package Name">
              {selectedRecord.pkg_name || "N/A"}
            </Descriptions.Item>
            <Descriptions.Item label="License Name">
              {selectedRecord.name}
            </Descriptions.Item>
            <Descriptions.Item label="Severity">
              <Tag
                color={
                  selectedRecord.severity === "HIGH"
                    ? "red"
                    : selectedRecord.severity === "MEDIUM"
                    ? "orange"
                    : selectedRecord.severity === "LOW"
                    ? "green"
                    : "gray"
                }
              >
                {selectedRecord.severity}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="File Path">
              {selectedRecord.file_path || "N/A"}
            </Descriptions.Item>
            <Descriptions.Item label="Link">
              {selectedRecord.link ? (
                <a
                  href={selectedRecord.link}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {selectedRecord.link}
                </a>
              ) : (
                "N/A"
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Details">
              {selectedRecord.text || "N/A"}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
}

export default LicenceOverview;
