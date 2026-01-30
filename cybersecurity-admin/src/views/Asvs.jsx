import React, { useState, useEffect, Suspense } from "react";
import {ConfigProvider,Table,Button,Modal,Form,Input,Popconfirm,message,Spin,} from "antd";
import { DeleteOutlined, EditOutlined, LinkOutlined } from "@ant-design/icons";
import {useFetchAsvsQuery,useAddAsvsMutation,useUpdateAsvsMutation,useDeleteAsvsMutation} from "../store/api/cyberService/asvsApi";
import { useFetchAsvsScannerTypeQuery } from "../store/api/cyberService/AsvsScannerTypesApi";
import LinkASVS from "../components/link/LinkASVS";

const Asvs = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editRecord, setEditRecord] = useState(null);
  const [form] = Form.useForm();
  const [isLinkModalVisible, setIsLinkModalVisible] = useState(false);
  const [linkRecord, setLinkRecord] = useState(null);
  const [selectedScannerTypes, setSelectedScannerTypes] = useState([]);

  const {data: asvsScannerTypeData,isLoading: isLoadingScannerTypeData,refetch: refetchAsvsScannerTypeData,} = useFetchAsvsScannerTypeQuery();
  const {data: asvsData,isLoading,refetch: refetchAsvsData,} = useFetchAsvsQuery();
  const [addAsvs, { isLoading: isAdding }] = useAddAsvsMutation();
  const [updateAsvs, { isLoading: isUpdating }] = useUpdateAsvsMutation();
  const [deleteAsvs] = useDeleteAsvsMutation();

  const onFinish = async (values) => {
    const payload = {
      chapter_id: values.chapter_id,
      chapter_name: values.chapter_name,
      section_id: values.section_id,
      section_name: values.section_name,
      requirement_id: values.requirement_id,
      requirement_name: values.requirement_name,
    };
    try {
      if (editRecord?._id) {
        await updateAsvs({ id: editRecord._id, asvsData: payload }).unwrap();
        message.success("ASVS updated successfully!");
      } else {
        await addAsvs([payload]).unwrap();
        message.success("ASVS added successfully!");
      }
      form.resetFields();
      setIsModalVisible(false);
    } catch (error) {
      console.log("error", error);
      message.error(
        error?.data?.error || "Failed to submit the ASVS. Please try again."
      );
    }
  };

  useEffect(() => {
    if (isLinkModalVisible && !asvsScannerTypeData) {
      refetchAsvsScannerTypeData();
    }
  }, [isLinkModalVisible, asvsScannerTypeData, refetchAsvsScannerTypeData]);
  

  const handleDelete = async (id) => {
    try {
      await deleteAsvs({ id }).unwrap();
      message.success("ASVS deleted successfully!");
    } catch {
      message.error("Failed to delete the ASVS. Please try again.");
    }
  };

  const handleEdit = (record) => {
    if (!record._id) {
      message.error("Invalid ASVS record selected!");
      return;
    }
    setEditRecord(record);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  const handleAdd = () => {
    setEditRecord(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const updateLinkedRecord = (updatedRecord) => {
    setTableData((prevData) =>
      prevData.map((item) =>
        item._id === updatedRecord._id ? { ...item, asvs_id: updatedRecord.scanner_types } : item
      )
    );
    setSelectedScannerTypes(updatedRecord.asvs_id?.map((s) => s.scan_type) || []);
    setIsLinkModalVisible(false);
    refetchframeworksData();
  };


  const handleLinkClick = (record) => {
    setLinkRecord(record);
    setIsLinkModalVisible(true);
  };

  const columns = [
    { title: "Chapter", dataIndex: "chapter_id", width: "1%", align: "center" },
    { title: "Chapter Name", dataIndex: "chapter_name", width: "12%" },
    { title: "Section", dataIndex: "section_id", width: "1%", align: "center" },
    { title: "Section Name", dataIndex: "section_name", width: "15%" },
    {
      title: "Requirements",
      dataIndex: "requirement_id",
      width: "1%",
      align: "center",
    },
    { title: "Requirements Name", dataIndex: "requirement_name", width: "30%" },
    {
      title: "Actions",
      width: "2%",
      render: (_, record) => (
        <div style={{ display: "flex", gap: "8px" }}>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button
            icon={<LinkOutlined />}
            onClick={() => handleLinkClick(record)}
          />
          <Popconfirm
            title="Are you sure you want to delete this ASVS?"
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
        <div style={{ fontSize: "20px", marginBottom: "10px" }}>
          ASVS (Application Security Verification Standard)
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "10px",
          }}
        >
          <Button type="primary" onClick={handleAdd}>
            Add New 
          </Button>
        </div>
        <Table
          columns={columns}
          style={{ marginTop: "20px" }}
          dataSource={asvsData?.data ? [...asvsData.data].reverse(): []}
          rowKey="_id"
          loading={isLoading}
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
              name="chapter_id"
              label="Chapter"
              rules={[{ required: true, message: "Please enter the Chapter" }]}
            >
              <Input placeholder="Enter the Chapter" />
            </Form.Item>
            <Form.Item
              name="chapter_name"
              label="Chapter Name"
              rules={[
                { required: true, message: "Please enter the Chapter Name" },
              ]}
            >
              <Input placeholder="Enter the Chapter Name" />
            </Form.Item>
            <Form.Item
              name="section_id"
              label="Section"
              rules={[{ required: true, message: "Please enter the Section" }]}
            >
              <Input placeholder="Enter the Sectio" />
            </Form.Item>
            <Form.Item
              name="section_name"
              label="Section Name"
              rules={[
                { required: true, message: "Please enter the Section Name" },
              ]}
            >
              <Input placeholder="Enter the Section Name" />
            </Form.Item>
            <Form.Item
              name="requirement_id"
              label="Requirements"
              rules={[
                { required: true, message: "Please enter the Requirements" },
              ]}
            >
              <Input placeholder="Enter the Requirements Name" />
            </Form.Item>
            <Form.Item
              name="requirement_name"
              label="Requirements Name"
              rules={[
                {
                  required: true,
                  message: "Please enter the Requirements Name",
                },
              ]}
            >
              <Input placeholder="Enter the version" />
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
        <Modal
          title="Link ASVS & Scanner Types"
          open={isLinkModalVisible}
          onCancel={() => setIsLinkModalVisible(false)}
          footer={null}
          width={900}
        >
          <Suspense fallback={<Spin tip="Loading LinkASVS..." />}>
            <LinkASVS
              record={linkRecord}
              selectedScannerTypes={selectedScannerTypes}
              setSelectedScannerTypes={setSelectedScannerTypes}
              updateLinkedRecord={updateLinkedRecord}
              refetchframeworksData={refetchAsvsData}
              onClose={() => setIsLinkModalVisible(false)}
              asvsScannerTypeData={asvsScannerTypeData}
            />
          </Suspense>
        </Modal>
      </div>
    </ConfigProvider>
  );
};

export default Asvs;
