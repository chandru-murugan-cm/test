import React, { useState, useEffect } from "react";
import { ConfigProvider, Table, Tabs, message, Button } from "antd";
import { useFetchScannerTypesQuery } from "../../store/api/cyberService/scantypeApi";
import { useGetScanTargetsQuery } from "../../store/api/cyberService/scantypeApi";
import { useAddFrameworkScannerTypeMutation, useUpdateFrameworkScannerTypeMutation } from "../../store/api/cyberService/FrameworkScannerTypesApi";

const LinkFS = ({ record, onClose, editRecord }) => {
  const [activeTab, setActiveTab] = useState(null);
  const [scanData, setScanData] = useState({});
  const [selectedItems, setSelectedItems] = useState({});
  const [submittedItems, setSubmittedItems] = useState({});

  const { data: scanTypeData } = useFetchScannerTypesQuery();
  const { data: scanTargets } = useGetScanTargetsQuery(activeTab);
  const [addFrameworkScannerType, { isLoading }] = useAddFrameworkScannerTypeMutation();
  const [updateFrameworkScannerType] = useUpdateFrameworkScannerTypeMutation();

  const tabItems = scanTargets?.scan_target_types?.map((type) => ({
    label: type,
    key: type,
  })) || [];

  useEffect(() => {
    if (scanTypeData) {
      const groupedData = Array.isArray(scanTypeData)
        ? scanTypeData.reduce((acc, item) => {
            const category = item.category || "Others";
            acc[category] = acc[category] || [];
            acc[category].push(item);
            return acc;
          }, {})
        : scanTypeData;
      setScanData(groupedData);
    }
  }, [scanTypeData]);

  useEffect(() => {
    if (!activeTab && tabItems?.length > 0) {
      setActiveTab(tabItems[0]?.key);
    }
  }, [tabItems]);

  useEffect(() => {
    if (record?.scanner_types) {
      const preSelected = record.scanner_types.reduce((acc, scanner) => {
        const { scan_target_type, _id } = scanner;
        if (!acc[scan_target_type]) acc[scan_target_type] = [];
        acc[scan_target_type].push(_id);
        return acc;
      }, {});
      setSelectedItems(preSelected);
      setSubmittedItems(preSelected);
    }
  }, [record]);
  

  const handleCheckboxChange = (selectedRowKeys) => {
    setSelectedItems((prev) => ({
      ...prev,
      [activeTab]: [...selectedRowKeys],
    }));
  };

  const handleSubmit = async () => {
    const payload = {
      framework_id: record._id,
      scanner_type_id: Object.values(selectedItems).flat(),
    };
    try {
      if (record?.framework_scanner_mapping?._id) {
        await updateFrameworkScannerType({
          frameworkId: record.framework_scanner_mapping._id,
          updatedData: payload,
        }).unwrap();
        message.success("Framework scanner types updated successfully.");
      } else {
        await addFrameworkScannerType(payload).unwrap();
        message.success("Scanner type added to Framework.");
      }
  
      setSubmittedItems(selectedItems);
      if (onClose) {
        onClose();
      }
    } catch (error) {
      message.error(error?.data?.error || "Failed to update Framework scanners.");
    }
  };

  const columns = [
    {
      title: "Scan Type",
      dataIndex: "scan_type",
      width: "90%",
      render: (text, record) => (
        <div>
          <strong>{text || "Unknown"}</strong>
          <p style={{ margin: 0, color: "#666", fontSize: "12px" }}>{record.description}</p>
        </div>
      ),
    },
  ];

  let filteredData = scanData?.data
    ? scanData.data.filter((item) => item.scan_target_type === activeTab)
    : [];

    if (submittedItems[activeTab]?.length > 0) {
      filteredData = [...filteredData].sort((a, b) => submittedItems[activeTab].includes(a._id) ? -1 : 1);
    }
  return (
    <ConfigProvider theme={{ token: { colorPrimary: "#6BE992" } }}>
      <div style={{ padding: "15px", marginTop: "20px" }}>
        <div style={{ display: "flex", justifyContent: "flex-start", width: "100%" }}>
          <Tabs
            activeKey={activeTab}
            onChange={(key) => setActiveTab(key)}
            items={tabItems}
            tabBarStyle={{ display: "flex", gap: "20px", paddingBottom: "10px", textTransform: "uppercase" }}
          />
        </div>
        <Table
          rowSelection={{
            type: "checkbox",
            columnTitle: "Select",
            selectedRowKeys: selectedItems[activeTab] || [],
            onChange: handleCheckboxChange,
            getCheckboxProps: (record) => ({
              defaultChecked: submittedItems[activeTab]?.includes(record._id) || false,
            }),
          }}
          columns={columns}
          dataSource={filteredData}
          rowKey="_id"
          pagination={false}
          bordered
          locale={{ emptyText: "No data available for this tab" }}
        />
        <Button type="primary" style={{ marginTop: "20px" }} onClick={handleSubmit} loading={isLoading}>Submit </Button>
      </div>
    </ConfigProvider>
  );
};

export default LinkFS;