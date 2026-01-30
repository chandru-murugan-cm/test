import React, { useState, useEffect } from "react";
import { ConfigProvider, Table, Tabs, message, Button } from "antd";
import { useFetchScannerTypesQuery, useGetScanTargetsQuery } from "../../store/api/cyberService/scantypeApi";
import { useAddOwasptoptenScannerTypesMutation, useUpdateOwasptoptenScannerTypesMutation } from "../../store/api/cyberService/OwaspTopTenScannerTypesApi";

const LinkOWASP = ({ record, onClose, OwaspTopTenScannerTypeData }) => {
  const [activeTab, setActiveTab] = useState(null);
  const [scanData, setScanData] = useState({});
  const [selectedItems, setSelectedItems] = useState({});
  const [submittedItems, setSubmittedItems] = useState({});

  const { data: scanTypeData } = useFetchScannerTypesQuery();
  const { data: scanTargets } = useGetScanTargetsQuery(activeTab);
  const [addOwasptoptenScannerTypes, { isLoading }] = useAddOwasptoptenScannerTypesMutation();
  const [updateOwasptoptenScannerTypes] = useUpdateOwasptoptenScannerTypesMutation();

  const handleSubmit = async () => {
    const payload = {
      owasp_top_ten_id: record._id,
      scanner_type_id: Object.values(selectedItems).flat(),
    };
    try {
      const existingMapping = OwaspTopTenScannerTypeData?.data?.find(
        (scanner) => scanner.owasp_top_ten_id === record._id
      );
      if (existingMapping) {
        await updateOwasptoptenScannerTypes({
          owasp_top_ten_id: existingMapping._id,
          updatedData: payload,
        }).unwrap();
        message.success("OWASP scanner types updated successfully.");
      } else {
        console.log("Adding new OWASP scanner mapping");
        await addOwasptoptenScannerTypes(payload).unwrap();
        message.success("Scanner type added to OWASP.");
      }
      setSubmittedItems(selectedItems);
      if (onClose) {
        onClose();
      }
    } catch (error) {
      console.error("Error updating OWASP scanners:", error);
      message.error(error?.data?.error || "Failed to update OWASP scanners.");
    }
};

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
    if (record?._id && OwaspTopTenScannerTypeData?.data?.length > 0) {
      const preSelected = OwaspTopTenScannerTypeData.data
        .filter((scanner) => scanner.owasp_top_ten_id === record._id)
        .reduce((acc, scanner) => {
          if (Array.isArray(scanner.scanner_type_id)) {
            scanner.scanner_type_id.forEach((id) => {
              const category = scanData?.data?.find(
                (item) => item._id === id
              )?.scan_target_type;
              if (category) {
                acc[category] = acc[category] ? [...acc[category], id] : [id];
              }
            });
          }
          return acc;
        }, {});
      setSelectedItems(preSelected);
      setSubmittedItems(preSelected);
    }
  }, [record, OwaspTopTenScannerTypeData, scanData]);
  const handleCheckboxChange = (selectedRowKeys) => {
    setSelectedItems((prev) => ({
      ...prev,
      [activeTab]: selectedRowKeys,
    }));
  };

  const columns = [
    { title: "Scan Type",dataIndex: "scan_type",width: "90%",
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
export default LinkOWASP;
