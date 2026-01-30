import React from "react";
import { Table, Tag, Spin, Empty } from "antd";
import { useFetchScannersQuery } from "../../store/api/cyberService/scannerApi";

const ScannerList = () => {
  const { data: scanners, isLoading, isError } = useFetchScannersQuery();

  // If there is an error, show a simple error message
  if (isError) {
    return (
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <Empty description="Error loading scanners." />
      </div>
    );
  }

  // If data is loading, show a simple loading spinner
  if (isLoading) {
    return (
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <Spin size="large" />
      </div>
    );
  }

  // Extract and flatten unique scanner types from the API response
  const allTypes = scanners?.data.flatMap((scanner) => scanner.type);
  const uniqueTypes = [...new Set(allTypes)]; // Get unique types

  // Columns for the table
  const columns = [
    {
      title: "S.No",
      dataIndex: "serial",
      key: "serial",
      render: (_, __, index) => index + 1, // Serial number based on row index
      width: "10%",
      align: "center", // Center serial number column
    },
    {
      title: "Scanner Type",
      dataIndex: "type",
      key: "type",
      render: (type) => type, // Simple tag with default styling
      align: "left", // Center the tags
    },
  ];

  // Prepare dataSource for the table
  const dataSource = uniqueTypes.map((type, index) => ({
    key: index,
    type,
  }));

  return (
    <div style={{ padding: "0", maxWidth: "500px", margin: "0" }}>
      {/* Table displaying unique scanner types */}
      <Table
        dataSource={dataSource} // Pass the unique types to the dataSource
        columns={columns}
        rowKey="key"
        pagination={false}
        bordered
      />
    </div>
  );
};

export default ScannerList;
