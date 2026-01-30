import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Table, Typography, message, Select, Spin } from "antd";
import { EyeOutlined } from "@ant-design/icons";
import moment from "moment";
import { useSelector } from "react-redux";
import { useFetchScansByProjectQuery } from "../../store/api/cyberService/scannerApi";

const { Title } = Typography;

const ScansByScanner = ({ showProjectColumn }) => {
  const navigate = useNavigate();
  const selectedProject = useSelector((state) => state.auth.selectedProject);

  const {
    data: scanResults,
    isLoading,
    error,
  } = useFetchScansByProjectQuery(selectedProject?._id, {
    skip: !selectedProject?._id,
  });

  // Prepare scan data for the table
  const unformattedScanResult =
    scanResults?.data.map((scan) => ({
      scanId: scan.unformatted_scan_results_id,
      projectName: scan.project_name,
      status: scan.status,
      scanTypes: scan.scanner_type_details?.join(", "),
      time: moment(scan.created).format("YYYY-MM-DD HH:mm"),
    })) || [];

  const columns = [
    {
      title: "S.No",
      dataIndex: "serial",
      key: "serial",
      render: (_, __, index) => index + 1,
      width: "10%",
      align: "center",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 150,
      align: "center",
      render: (text) => (
        <span style={{ textTransform: "capitalize" }}>{text}</span>
      ),
    },
    {
      title: "Scan Types",
      dataIndex: "scanTypes",
      key: "scanTypes",
      width: 200,
      align: "center",
      render: (text) => {
        const scanners = text?.split(", ");
        const displayScanners = scanners?.slice(0, 2).join(", ");
        const moreScanners = scanners?.length > 2 ? "..." : "";
        return (
          <span>
            {displayScanners}
            {moreScanners && <span> {moreScanners}</span>}
          </span>
        );
      },
    },
    {
      title: "Scanned Time",
      dataIndex: "time",
      key: "time",
      width: 200,
      align: "center",
    },
  ].filter(Boolean);

  return (
    <div style={{ padding: "0 20px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        Scans
      </Title>

      {isLoading ? (
        <Spin />
      ) : (
        <Table
          columns={columns}
          dataSource={unformattedScanResult}
          rowKey="scanId"
          pagination={false}
          bordered
          style={{ backgroundColor: "#fff", borderRadius: "8px" }}
          size="middle"
        />
      )}
      {error && message.error("Error fetching scans.")}
    </div>
  );
};

export default ScansByScanner;
