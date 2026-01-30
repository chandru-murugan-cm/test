// ScanTable.js
import React from "react";
import { Table } from "antd";

const ScanTable = ({ data }) => {
  // Columns for the latest scan table
  const columns = [
    {
      title: "Project Name",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "Website URL",
      dataIndex: "domain_value",
      key: "domain_value",
    },
    {
      title: "Github URL",
      dataIndex: "repo_url",
      key: "repo_url",
    },
    {
      title: "Start Date",
      dataIndex: "created",
      key: "created",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => {
        let color;
        if (status === "Completed") {
          color = "green";
        } else if (status === "Running") {
          color = "blue";
        } else {
          color = "red";
        }
        return <span style={{ color, fontWeight: "bold" }}>{status}</span>;
      },
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      pagination={false}
      bordered
      rowClassName={(record, index) =>
        index % 2 === 0 ? "table-row-light" : "table-row-dark"
      }
      style={{
        borderRadius: "10px",
        boxShadow: "0 2px 10px rgba(0, 0, 0, 0.1)",
      }}
    />
  );
};

export default ScanTable;
