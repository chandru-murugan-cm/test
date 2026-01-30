import React from "react";
import { Table, Tag, Tooltip } from "antd";
import {
  BugOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
  GithubOutlined,
  LockOutlined,
  FileSearchOutlined,
  CodeOutlined,
  GlobalOutlined,
  LinkOutlined,
  ClusterOutlined,
  CloudOutlined
} from "@ant-design/icons";
import moment from "moment";

const getScanTypeIcon = (scanType) => {
  const iconMap = {
    "Secrets Detection": <LockOutlined style={{ fontSize: "20px" }} />,
    "Smart Contract Vulnerability Scanner": <ClusterOutlined style={{ fontSize: "20px" }} />,
    "Licenses and SBOM": <FileSearchOutlined style={{ fontSize: "20px" }} />,
    "Dependency Vulnerability Scanner": (
      <CodeOutlined style={{ fontSize: "20px" }} />
    ),
    "Languages and Framework": <CodeOutlined style={{ fontSize: "20px" }} />,
  };

  return (
    iconMap[scanType] || (
      <LinkOutlined style={{ fontSize: "20px", color: "#6C757D" }} />
    )
  );
};

const FindingsTable = ({
  filteredFindings,
  loading,
  onRowClick,
  setDrawerVisible,
  currentPage,
  pageSize,
  onPageChange,
  totalPages,
  setPageSize,
}) => {
  const columns = [
    {
      title: "Finding Date",
      dataIndex: "finding_date",
      key: "finding_date",
      render: (date) => (
        <div style={{ padding: "10px 14px" }}>
          <span style={{ fontSize: "14px" }}>
            {moment(date).format("MMM D, YYYY hh:mm A")}
          </span>
        </div>
      ),
      width: 120,
    },
    {
      title: "Target",
      dataIndex: "targetType",
      key: "target_id",
      render: (text, record) => {
        const isRepo = record.target_type === "repo";
        const isContract = record.target_type === "web3";
        const isCloud = record.target_type === "cloud";
        return (
          <div style={{ padding: "10px 14px" }}>
            <Tooltip title={text}>
              <span
                style={{
                  display: "block",
                  maxWidth: "180px",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  fontSize: "14px",
                  color: "#113032",
                  // Target text color
                }}
              >
                {isRepo ? (
                  <GithubOutlined
                    style={{ marginRight: 8, color: "#113032" }}
                  />
                ) : isCloud ? (
                  <CloudOutlined
                    style={{ marginRight: 8, color: "#113032" }}
                  />
                ) : isContract ? (
                  <ClusterOutlined
                    style={{ marginRight: 8, color: "#113032" }}
                  />
                ) : (
                  <GlobalOutlined
                    style={{ marginRight: 8, color: "#113032" }}
                  />
                )}
                {text}
              </span>
            </Tooltip>
          </div>
        );
      },
      onCell: () => ({
        style: {
          padding: "10px 14px", // Remove padding from the cell
          height: "100%", // Ensure the cell uses the full height
        },
      }),
      width: 150,
    },
    {
      title: "Scan Type",
      dataIndex: "scanType",
      key: "scan_type_id",
      render: (scanType) => {
        const maxLength = 30; // Set the maximum length for truncation
        const isLongText = scanType.length > maxLength; // Check if the text is too long

        return (
          <div style={{ padding: "10px 14px" }}>
            <span
              style={{
                fontSize: "14px",
                display: "flex",
                alignItems: "center",
                maxWidth: "240px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {getScanTypeIcon(scanType)}
              <span
                style={{
                  marginLeft: "8px",
                  fontSize: "13px",
                  maxWidth: "200px",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {isLongText
                  ? `${scanType.substring(0, maxLength)}...`
                  : scanType}
              </span>
              {isLongText && (
                <Tooltip title={scanType}>
                  <ExclamationCircleOutlined
                    style={{
                      fontSize: "14px",
                      marginLeft: "8px",
                      color: "#6C757D",
                      cursor: "pointer",
                    }}
                  />
                </Tooltip>
              )}
            </span>
          </div>
        );
      },
      onCell: () => ({
        style: {
          padding: "10px 14px",
          height: "100%",
        },
      }),
      width: 240,
    },

    {
      title: "Finding",
      dataIndex: "finding_name",
      key: "finding_name",
      render: (text, record) => (
        <div
          style={{
            maxWidth: "300px",
            wordWrap: "break-word",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            fontSize: "14px",
            padding: "10px 14px",
          }}
        >
          {text}
          <div
            style={{
              marginTop: 5,
              color: "#888",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              maxWidth: "300px",
              fontSize: "13px", // Adjusted font size for description
            }}
          >
            {record.finding_desc}
          </div>
        </div>
      ),
      onCell: () => ({
        style: {
          padding: "10px 14px", // Remove padding from the cell
          height: "100%", // Ensure the cell uses the full height
        },
      }),
      width: 300,
    },
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      render: (severity) => {
        const colorMap = {
          high: "#FFCCCC",
          critical: "#FFCCCC",
          medium: "#CCE5FF",
          low: "#D4EDDA",
          informational: "#f2f55f2",
        };
        const textColorMap = {
          high: "#B71C1C",
          critical: "#B71C1C",
          medium: "#0D47A1",
          low: "#1B5E20",
          informational: "#000",
        };
        const iconMap = {
          high: <WarningOutlined />,
          critical: <ExclamationCircleOutlined />,
          medium: <ExclamationCircleOutlined />,
          low: <CheckCircleOutlined />,
        };

        return (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: colorMap[severity],
              color: textColorMap[severity],
              fontWeight: "400",
              fontSize: "14px",
              height: "70px",
              width: "100%",
              textTransform: "capitalize",
              padding: "0", // Remove padding
            }}
          >
            <span style={{ marginRight: "8px" }}>{iconMap[severity]}</span>
            {severity}
          </div>
        );
      },
      onCell: () => ({
        style: {
          padding: "0px !important", // Remove padding from the cell
          height: "100%", // Ensure the cell uses the full height
        },
      }),
      width: 100,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => {
        const colorMap = {
          open: "#FFF3CD",
          closed: "#D4EDDA",
          "false positive": "#F8D7DA",
          ignored: "#E2E3E5",
        };
        const textColorMap = {
          open: "#856404",
          closed: "#155724",
          "false positive": "#721C24",
          ignored: "#6C757D",
        };
        const iconMap = {
          open: <BugOutlined />,
          closed: <CheckCircleOutlined />,
          "false positive": <ExclamationCircleOutlined />,
          ignored: <LockOutlined />,
        };

        return (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: colorMap[status] || "#FFFFFF",
              color: textColorMap[status] || "#000000",
              fontWeight: "400",
              fontSize: "14px",
              height: "70px",
              width: "100%",
              textTransform: "capitalize",
              padding: "0",
            }}
          >
            <span style={{ marginRight: "8px" }}>{iconMap[status]}</span>
            {status}
          </div>
        );
      },
      onCell: () => ({
        style: {
          padding: "0px",
          height: "100%",
        },
      }),
      width: 100,
    },
  ];

  return (
    <Table
      dataSource={filteredFindings}
      columns={columns}
      loading={loading}
      onRow={(record) => ({
        onClick: () => {
          onRowClick(record), setDrawerVisible(true);
        },
      })}
      style={{ cursor: "pointer" }}
      bordered
      pagination={
        onRowClick !== ""
          ? {
              current: currentPage,
              pageSize,
              total: totalPages * pageSize,
              onChange: (page, newPageSize) => {
                onPageChange(page);
                if (newPageSize !== pageSize) {
                  setPageSize(newPageSize);
                }
              },
            }
          : false
      }
      // Column header style adjustment
      components={{
        header: {
          cell: ({ children, ...restProps }) => (
            <th
              {...restProps}
              style={{
                fontSize: "15px",
                fontWeight: "600",
                padding: "10px 14px", // Remove padding for header cells
              }}
            >
              {children}
            </th>
          ),
        },
        body: {
          cell: ({ children, ...restProps }) => (
            <td
              {...restProps}
              style={{
                padding: "0px",
                height: "100%",
                background: "transparent",
              }}
            >
              {children}
            </td>
          ),
        },
      }}
    />
  );
};

export default FindingsTable;
