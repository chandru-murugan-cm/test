import React from "react";
import { Table, Tag } from "antd"; 
import { useFetchLicensesGroupByTypeAndRiskQuery } from "../../store/api/cyberService/repoScanResultsApi.js";

function LicenceGroups({ project_id }) {
  const {
    data: licensesGroupedData, // The response data
    error, // Error state
    isLoading, // Loading state
  } = useFetchLicensesGroupByTypeAndRiskQuery(project_id);

  // Handle loading state
  if (isLoading) return <div>Loading...</div>;

  // Handle error state
  if (error) return <div>Error fetching licenses data!</div>;

  // Define filters for the risk levels (including "UNKNOWN")
  const riskFilters = [
    { text: "High", value: "HIGH" },
    { text: "Medium", value: "MEDIUM" },
    { text: "Low", value: "LOW" },
    { text: "Unknown", value: "UNKNOWN" },
  ];

  // Define color coding based on risk level
  const getRiskTagColor = (risk_level) => {
    switch (risk_level) {
      case "HIGH":
        return "volcano";
      case "MEDIUM":
        return "gold";
      case "LOW":
        return "green";
      case "UNKNOWN":
        return "grey"; 
      default:
        return "blue"; 
    }
  };

  // Format risk level to title case for display purposes
  const formatRiskLevel = (risk_level) => {
    return risk_level.charAt(0) + risk_level.slice(1).toLowerCase();
  };

  // Define columns for the Ant Design table
  const columns = [
    {
      title: "Package",
      dataIndex: "license_type", // Field name from data
      key: "license_type",
      filters: [...new Set(licensesGroupedData?.data.map((group) => group._id.pkg_name))].map((name) => ({
        text: name,
        value: name,
      })), // Dynamically generate filters based on license types
      onFilter: (value, record) => record.license_type.includes(value), // Filter logic
      render: (license_type) => {
        // Check if license_type is an array and safely join
        return Array.isArray(license_type) ? license_type.join(", ") : license_type;
      },
    },
    // {
    //   title: "Risk Level",
    //   dataIndex: "risk_level",
    //   key: "risk_level",
    //   filters: riskFilters, // Apply filters for the risk level
    //   onFilter: (value, record) => record.risk_level === value, // Filter logic for risk level
    //   render: (risk_level) => (
    //     <Tag color={getRiskTagColor(risk_level)}>{formatRiskLevel(risk_level)}</Tag>
    //   ), // Add color coding and format risk level to title case
    // },
    {
      title: "Count",
      dataIndex: "count",
      key: "count",
      sorter: (a, b) => a.count - b.count, // Sort logic for count
    },
  ];

  // Map the data to fit the table's columns
  const dataSource =
    licensesGroupedData?.data.map((group) => ({
      license_type: group._id.pkg_name, // You can choose how to display this (e.g., `pkg_name` or `category`)
      risk_level: group._id.severity, // You can choose to display severity or another field
      count: group.total_count, // The total count of licenses
    })) || [];

  // Render the table
  return <Table columns={columns} dataSource={dataSource} rowKey="license_type" />;
}

export default LicenceGroups;
