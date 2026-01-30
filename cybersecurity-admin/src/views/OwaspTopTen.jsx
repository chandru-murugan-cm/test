import React, { useState, useEffect, Suspense } from "react";
import {ConfigProvider,Table,Button,Modal,Form,Input,Popconfirm,message,Spin,} from "antd";
import { DeleteOutlined, EditOutlined, LinkOutlined } from "@ant-design/icons";
import {useFetchOwaspTopTenQuery,useAddOwaspTopTenMutation,useUpdateOwaspTopTenMutation,useDeleteOwaspTopTenMutation,} from "../store/api/cyberService/OwaspTopTen";
import { useFetchOwasptoptenScannerTypeQuery } from "../store/api/cyberService/OwaspTopTenScannerTypesApi";
import LinkOWASP from "../components/link/LinkOWASP";

const OwaspTopTen = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editRecord, setEditRecord] = useState(null);
  const [form] = Form.useForm();
  const [isLinkModalVisible, setIsLinkModalVisible] = useState(false);
  const [linkRecord, setLinkRecord] = useState(null);
  const [selectedScannerTypes, setSelectedScannerTypes] = useState([]);

  const {data: OwaspTopTenScannerTypeData, isLoading: isLoadingScannerTypeData,refetch: refetchOwaspTopTenScannerTypeData,} = useFetchOwasptoptenScannerTypeQuery();
  const {data: OwaspTopTenData,isLoading,refetch: refetchOwaspTopTenData,} = useFetchOwaspTopTenQuery();
  const [addOwaspTopTen, { isLoading: isAdding }] = useAddOwaspTopTenMutation();
  const [updateOwaspTopTen, { isLoading: isUpdating }] = useUpdateOwaspTopTenMutation();
  const [deleteOwaspTopTen] = useDeleteOwaspTopTenMutation();

  const onFinish = async (values) => {
    const payload = {
      control_name: values.control_name,
      group_name: values.group_name,
    };
  
    try {
      if (editRecord?._id) {
        await updateOwaspTopTen({
          owasp_top_ten_id: editRecord._id,
          updatedData: payload,
        }).unwrap();
  
        message.success("OWASP updated successfully!");
        setIsModalVisible(false); 
        form.resetFields(); 
      } else {
        await addOwaspTopTen(payload)
          .then(() => {
            message.success("OWASP added successfully!");
            setIsModalVisible(false); 
            form.resetFields();
          })
          .catch((error) => {
            message.error(
              error?.data?.error ||
                "Failed to submit the OwaspTopTen. Please try again."
            );
          });
      }
    } catch (error) {
      message.error(
        error?.data?.error || "Failed to submit the OwaspTopTen. Please try again."
      );
    }
  };
  
  useEffect(() => {
    if (isLinkModalVisible && !OwaspTopTenScannerTypeData) {
      refetchOwaspTopTenScannerTypeData();
    }
  }, [isLinkModalVisible,OwaspTopTenScannerTypeData,refetchOwaspTopTenScannerTypeData]);

  const handleDelete = async (id) => {
    if (!id || typeof id !== "string") {message.error("Invalid record ID!");
      return;
    }  
    try {
      await deleteOwaspTopTen(id).unwrap(); 
      message.success("OWASP deleted successfully!");
      refetchOwaspTopTenData(); 
    } catch (error) {
      message.error(error?.data?.error || "Failed to delete the OWASP. Please try again.");
    }
  };
  
  const handleEdit = (record) => {
    if (!record._id) {
      message.error("Invalid OwaspTopTen record selected!");
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
        item._id === updatedRecord._id? { ...item, owasp_top_ten_id: updatedRecord.scanner_types}: item
      )
    );
    setSelectedScannerTypes(updatedRecord.owasp_top_ten_id?.map((s) => s.scan_type) || []
    );
    setIsLinkModalVisible(false);
    refetchframeworksData();
  };

  const handleLinkClick = (record) => {
    setLinkRecord(record);
    setIsLinkModalVisible(true);
  };

  const columns = [
    { title: "Control Name", dataIndex: "control_name" },
    { title: "Group Name", dataIndex: "group_name" },
    {
      title: "Actions",
      render: (_, record) => (
        <div style={{ display: "flex", gap: "8px" }}>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button
            icon={<LinkOutlined />}
            onClick={() => handleLinkClick(record)}
          />
          <Popconfirm
            title="Are you sure you want to delete this OWASP?"
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
        <div style={{ fontSize: "20px", marginBottom: "10px" }}>OwaspTopTen (Open Web Application Security Project Top Ten)</div>
        <div
          style={{display: "flex",justifyContent: "flex-end",marginBottom: "10px"}}>
          <Button type="primary" onClick={handleAdd}>Add New </Button>
        </div>
        <Table
          columns={columns}
          style={{ marginTop: "20px" }}
          dataSource={
            OwaspTopTenData?.data ? [...OwaspTopTenData.data].reverse() : []
          }
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
              name="control_name"
              label="Control Name"
              rules={[{ required: true, message: "Please enter the Control Name" },]}
            >
              <Input placeholder="Enter the Control Name" />
            </Form.Item>
            <Form.Item
              name="group_name"
              label="Group Name"
              rules={[{ required: true, message: "Please enter the Group Name" },]}
            >
              <Input placeholder="Enter the Group Name" />
            </Form.Item>
            <div
              style={{display: "flex",justifyContent: "flex-end",gap: "8px",}}
            >
              <Button onClick={() => setIsModalVisible(false)}>Cancel</Button>
              <Button
                type="primary"
                htmlType="submit"
                loading={isAdding || isUpdating}
              >Submit
              </Button>
            </div>
          </Form>
        </Modal>
        <Modal
          title="Link OwaspTopTen & Scanner Types"
          open={isLinkModalVisible}
          onCancel={() => setIsLinkModalVisible(false)}
          footer={null}
          width={900}
        >
          <Suspense fallback={<Spin tip="Loading LinkOwaspTopTen..." />}>
            <LinkOWASP
              record={linkRecord}
              selectedScannerTypes={selectedScannerTypes}
              setSelectedScannerTypes={setSelectedScannerTypes}
              updateLinkedRecord={updateLinkedRecord}
              refetchframeworksData={refetchOwaspTopTenData}
              onClose={() => setIsLinkModalVisible(false)}
              OwaspTopTenScannerTypeData={OwaspTopTenScannerTypeData}
            />
          </Suspense>
        </Modal>
      </div>
    </ConfigProvider>
  );
};

export default OwaspTopTen;
