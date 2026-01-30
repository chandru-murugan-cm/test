import React, { useState, useEffect } from "react";
import { ConfigProvider, Table, Button, Modal, Form, Input, Checkbox, message, Select, Popconfirm, Tabs } from "antd";
import { DeleteOutlined, EditOutlined } from "@ant-design/icons";
import { useFetchScannerTypesQuery, useAddScannerMutation, useUpdateScannerMutation, useDeleteScannerMutation, useGetScanTargetsQuery } from "../store/api/cyberService/scantypeApi";
import { useFetchScannersQuery } from "../store/api/cyberService/scannerApi";

const ScanType = () => {
  const [activeTab, setActiveTab] = useState(null),
    [scanData, setScanData] = useState({}),
    [selectedItems, setSelectedItems] = useState([]),
    [scannerTypes, setScannerTypes] = useState([]),
    [isModalVisible, setIsModalVisible] = useState(false),
    [editRecord, setEditRecord] = useState(null),
    [targetType, setTargetType] = useState(null), // Track the selected target type
    [form] = Form.useForm();

  const { data: scanTypeData } = useFetchScannerTypesQuery();
  const { data: scannerData } = useFetchScannersQuery();
  const { data: scanTargets, isLoadingType } = useGetScanTargetsQuery(activeTab); 
  const [addScanner, { isLoading: isAdding }] = useAddScannerMutation();
  const [updateScanner, { isLoading: isUpdating }] = useUpdateScannerMutation();
  const [deleteScanner] = useDeleteScannerMutation();

  const onFinish = async (values) => {
    try {
      const payload = {
        description: values.description,
        scan_target_type: values.scan_target_type,
        scanner_ids: values.selectedScanners,
        scan_type: values.scan_type,
        cloud_provider: values.cloud_provider , // Include cloud_provider if present
      };
      if (editRecord) {
        await updateScanner({ scannerData: payload, id: editRecord._id }).unwrap();
        message.success("Scanner updated successfully!");
      } else {
        const updatepayload = {
          scan_types: [payload],
        };
        const newScanner = await addScanner(updatepayload).unwrap();
        message.success("Scanner added successfully!");
      }
      form.resetFields();
      setIsModalVisible(false);
    } catch (error) {
      message.error("Failed to submit the scanner. Please try again.");
    }
  };

  const tabItems = scanTargets?.scan_target_types?.map(type => ({
    label: type,
    key: type,
  })) 

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
    if (!activeTab && tabItems?.length > 0) {
      setActiveTab(tabItems[1]?.key); 
    }
  }, [scanTypeData, scannerData, activeTab, tabItems]);

  const handleAdd = () => {
    setEditRecord(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await deleteScanner({ id }).unwrap();
      setScanData((prev) => ({
        ...prev,
        [activeTab]: Array.isArray(prev[activeTab])
          ? prev[activeTab].filter((item) => item._id !== id)
          : [],
      }));
      setScannerTypes((prev) => prev.filter((item) => item._id !== id));
      message.success("Scanner deleted successfully!");
    } catch {
      message.error("Failed to delete the scanner. Please try again.");
    }
  };

  const handleEdit = (record) => {
    setEditRecord(record);
    const selectedScanners = record.scanner_ids || [];
    form.setFieldsValue({
      ...record,
      selectedScanners,
    });
    setIsModalVisible(true);
  };

  const columns = [
    { title: "Scan Type", dataIndex: "scan_type", width: "14%" },
    { title: "Description", dataIndex: "description" },
    {
      title: "Actions",
      render: (_, record) => (
        <div style={{ display: "flex", gap: "8px" }}>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="Are you sure you want to delete this scanner?" onConfirm={() => handleDelete(record._id)}>
            <Button icon={<DeleteOutlined />} style={{ color: "red" }} />
          </Popconfirm>
        </div>
      ),
    },
  ];

  return (
    <ConfigProvider theme={{ token: { colorPrimary: "#6BE992" } }}>
      <div style={{ padding: "15px", marginTop: "20px" }}>
        <div style={{ fontSize: "20px", marginBottom: "20px" }}>Scan Type</div>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "30px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "flex-start",
              width: "100%",
            }}
          >
            <Tabs
              activeKey={activeTab}
              onChange={(key) => setActiveTab(key)}
              items={tabItems}
              tabBarStyle={{
                display: "flex",
                gap: "20px",
                paddingBottom: "10px",
                textTransform: "uppercase",
              }}
            />
          </div>
          <Button type="primary" onClick={handleAdd}>Add Scan Type</Button>
        </div>
        <Table
          columns={columns}
          dataSource={scanData?.data? scanData.data.filter(
                  (item) => item.scan_target_type === activeTab).reverse()
              : []
          }
          rowKey="_id"
          pagination={false}
          bordered
          locale={{ emptyText: "No data available for this tab" }} 
        />
        <Modal
          title={editRecord ? "Edit Record" : "Add Record"}
          open={isModalVisible}
          onCancel={() => setIsModalVisible(false)}
          footer={null}
        >
          <Form
            layout="vertical"
            form={form}
            onFinish={onFinish}
            onValuesChange={(changedValues) => {
              if (changedValues.scan_target_type) {
                setTargetType(changedValues.scan_target_type); // Update the state when target type changes
                form.setFieldsValue({ cloud_provider: undefined }); // Reset cloud provider when target type changes
              }
            }}
          >
            <Form.Item
              name="scan_target_type"
              label="Target Type"
              rules={[
                { required: true, message: "Please select the target type" },
              ]}
            >
              <Select placeholder="Select Target Type" loading={isLoadingType}>
                {scanTargets?.scan_target_types?.map((type) => (
                  <Select.Option key={type} value={type}>
                    {type}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            {/* Conditionally render the cloud provider dropdown */}
            {targetType === "cloud" && (
              <Form.Item
                name="cloud_provider"
                label="Choose Cloud"
                rules={[
                  { required: true, message: "Please select a cloud provider" },
                ]}
              >
                <Select placeholder="Select Cloud Provider">
                  <Select.Option value="GCP">GCP</Select.Option>
                  <Select.Option value="Azure">Azure</Select.Option>
                </Select>
              </Form.Item>
            )}

            <Form.Item
              name="scan_type"
              label="Scan Type"
              rules={[
                { required: true, message: "Please enter the scan type" },
              ]}
            >
              <Input placeholder="Enter the scan type" />
            </Form.Item>
            <Form.Item
              name="description"
              label="Description"
              rules={[
                { required: true, message: "Please enter the description" },
              ]}
            >
              <Input.TextArea
                rows={4}
                placeholder="Enter a brief description"
              />
            </Form.Item>
            <Form.Item
              name="selectedScanners"
              label="Select Scanners"
              rules={[
                {
                  required: true,
                  message: "Please select at least one scanner type",
                },
              ]}
            >
              <Checkbox.Group>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>
                  {scannerData?.data?.map((scanner) => (
                    <div key={scanner._id} style={{ flexBasis: "48%" }}>
                      <Checkbox value={scanner._id}>
                        {scanner.name} Scanner
                      </Checkbox>
                    </div>
                  ))}
                </div>
              </Checkbox.Group>
            </Form.Item>
            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                gap: "8px",
              }}
            >
              <Button onClick={() => setIsModalVisible(false)}>Cancel</Button>
              <Button
                type="primary"
                htmlType="submit"
                loading={isAdding || isUpdating}
              >
                Submit
              </Button>
            </div>
          </Form>
        </Modal>
      </div>
    </ConfigProvider>
  );
};

export default ScanType;
