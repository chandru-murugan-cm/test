import React, { useState, useEffect } from "react";
import { ConfigProvider, Table, Button, Modal, Form, Input, Checkbox, Popconfirm, message } from "antd";
import { DeleteOutlined, EditOutlined } from "@ant-design/icons";
import { useFetchScannersQuery, useAddScannersMutation, useUpdateScannersMutation, useDeleteScannersMutation } from "../store/api/cyberService/scannerApi";

const ScannersData = () => {
  const [activeTab, setActiveTab] = useState(null);
  const [scanData, setScanData] = useState({});
  const [selectedItems, setSelectedItems] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editRecord, setEditRecord] = useState(null);
  const [form] = Form.useForm();
  const { data: scannerData } = useFetchScannersQuery();
  const [addScanners, { isLoading: isAdding }] = useAddScannersMutation();
  const [updateScanners, { isLoading: isUpdating }] = useUpdateScannersMutation();
  const [deleteScanners] = useDeleteScannersMutation();

  const onFinish = async (values) => {
    try {
      const payload = {
        description: values.description,
        name: values.name,
        version: values.version,
      };
      if (editRecord) {
        const response = await updateScanners({ scannerData: payload, id: editRecord._id }).unwrap();
        message.success("Scanner updated successfully!");
      } else {
        const newScanner = await addScanners(payload).unwrap();
        message.success("Scanner added successfully!");
      }
      form.resetFields();
      setIsModalVisible(false);
    } catch {
      message.error("Failed to submit the scanner. Please try again.");
    }
  };

  useEffect(() => {
    if (scannerData) {
      const groupedData = Array.isArray(scannerData)
        ? scannerData.reduce((acc, item) => {
            const category = item.category || "Others";
            acc[category] = acc[category] || [];
            acc[category].push(item);
            return acc;
          }, {})
        : {};
      setScanData(groupedData);
    }
  }, [scannerData]);

  const handleAdd = () => {
    setEditRecord(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await deleteScanners({ id }).unwrap();
      setScanData((prev) => ({
        ...prev,
        [activeTab]: (prev[activeTab] || []).filter((item) => item._id !== id),
      }));
      message.success("Scanner deleted successfully!");
    } catch {
      message.error("Failed to delete the scanner. Please try again.");
    }
  };

  const handleEdit = (record) => {
    setEditRecord(record);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  const columns = [
  
    { title: "Scanner Name", dataIndex: "name" },
    { title: "Description", dataIndex: "description" },
    { title: "Version", dataIndex: "version" },
    {
      title: "Actions",
      render: (_, record) => (
        <div style={{ display: "flex", gap: "8px" }}>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm
            title="Are you sure you want to delete this scanner?"
            onConfirm={() => handleDelete(record._id)}
          >
            <Button icon={<DeleteOutlined />} style={{ color: "red" }} />
          </Popconfirm>
        </div>
      ),
    },
  ];

  return (
    <ConfigProvider theme={{ token: { colorPrimary: "#6BE992" } }}>
      <div style={{ padding: "15px" }}>
        <div style={{ fontSize: "20px", marginBottom: "0px" }}>
          Scanners Data
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "10px",
          }}
        >
          <Button type="primary" onClick={handleAdd}>
            Add New Scan
          </Button>
        </div>
        <Table
          columns={columns}
          dataSource={scannerData?.data ? [...scannerData.data].reverse() : []}
          rowKey="id"
          pagination={false}
          bordered
        />
        <Modal
          title={editRecord ? "Edit Record" : "Add Record"}
          open={isModalVisible}
          onCancel={() => setIsModalVisible(false)}
          footer={null}
        >
          <Form layout="vertical" form={form} onFinish={onFinish}>
            <Form.Item
              name="name"
              label="Scanner Name"
              rules={[
                { required: true, message: "Please enter the scan type" },
              ]}
            >
              <Input placeholder="Enter the scan type" />
            </Form.Item>
            <Form.Item
              name="version"
              label="Version"
              rules={[{ required: true, message: "Please enter the version" }]}
            >
              <Input placeholder="Enter the version" />
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

export default ScannersData;
