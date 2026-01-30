import React from "react";
import { Table, Tooltip, Space } from "antd";
import {
  EyeOutlined,
  ScheduleOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import moment from "moment";

const ProjectTable = ({
  projects,
  navigate,
  handleScanNow,
  handleScheduleScanner,
}) => {
  const columns = [
    {
      title: "Project Name",
      dataIndex: "name",
      width: 140,
      key: "name",
    },
    {
      title: "Website URL",
      dataIndex: "domain_value",
      key: "domain_value",
    },
    {
      title: "GitHub URL",
      dataIndex: "repo_url",
      key: "repo_url",
    },
    {
      key: "created",
      title: "Created",
      dataIndex: "created",
      render: (record) => (
        <span>
          {record
            ? moment.utc(record).local().format("DD MMM, YYYY @ hh:mm:ss")
            : undefined}
        </span>
      ),
    },
    {
      title: "Action",
      key: "action",
      render: (_, record) => (
        <Space>
          <Tooltip title="View Project">
            <EyeOutlined
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/projects/${record._id}`);
              }}
              style={{ cursor: "pointer", color: "#1890ff" }}
            />
          </Tooltip>
          <Tooltip title="Scan Now">
            <ThunderboltOutlined
              onClick={(e) => {
                e.stopPropagation();
                handleScanNow(record.key);
              }}
              style={{ cursor: "pointer", color: "#52c41a" }}
            />
          </Tooltip>
          <Tooltip title="Schedule Scan">
            <ScheduleOutlined
              onClick={(e) => {
                e.stopPropagation();
                handleScheduleScanner(record.key);
              }}
              style={{ cursor: "pointer", color: "#fa8c16" }}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={projects}
      onRow={(record) => ({
        onClick: () => navigate(`/projects/${record._id}`),
      })}
      style={{ cursor: "pointer", color: "#1890ff" }}
    />
  );
};

export default ProjectTable;
