import React from "react";
import { Table, Spin, message, Typography } from "antd";
import { useFetchScannerTypesQuery } from "../../store/api/cyberService/scannerApi";

const { Title } = Typography;

const ScanTypeTable = ({ targetTypes, pagination }) => {
  const { data, isLoading, error } = useFetchScannerTypesQuery();

  if (error) {
    message.error("Failed to fetch scan types");
  }

  const filteredScanTypes = targetTypes?.map((targetType) => {
    return {
      targetType,
      scanTypes:
        data?.data?.filter(
          (scanner) => scanner.scan_target_type === targetType
        ) || [],
    };
  });

  const columns = [
    {
      title: "Scan Type",
      dataIndex: "scan_type",
      key: "scan_type",
      render: (text, record) => (
        <div
          style={{
            wordWrap: "break-word",
            whiteSpace: "wrap",
            fontSize: "14px",
            padding: "10px 14px",
          }}
        >
          {text}
          <div
            style={{
              marginTop: 5,
              color: "#888",
              whiteSpace: "wrap",
              fontSize: "13px",
            }}
          >
            {record.description}
          </div>
        </div>
      ),
      onCell: () => ({
        style: {
          padding: "10px 14px",
          height: "100%",
        },
      }),
    },
  ];

  if (isLoading) {
    return <Spin size="large" />;
  }

  return (
    <div>
      {filteredScanTypes?.length > 0 &&
        filteredScanTypes?.map(({ targetType, scanTypes }) => (
          <div key={targetType}>
            <Title
              level={5}
              style={{
                marginBottom: "15px",
                marginTop: "25px",
                textTransform: "capitalize",
              }}
            >
              Included Scan Types
            </Title>
            {scanTypes.length > 0 ? (
              <Table
                dataSource={scanTypes}
                columns={columns}
                rowKey="_id"
                pagination={pagination}
                bordered
                showHeader={false} // Hides the table header
              />
            ) : (
              <p>No scan types available for this {targetType}.</p>
            )}
          </div>
        ))}
    </div>
  );
};

export default ScanTypeTable;
