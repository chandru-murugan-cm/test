import React, { useState, useEffect, Suspense } from "react";
import { ConfigProvider, Table, Button, Modal, Form, Popconfirm, message, Tabs, Spin,Select,Input} from "antd";
import { DeleteOutlined, LinkOutlined,EditOutlined } from "@ant-design/icons";
import {
  useFetchCompliancesQuery,
  useFetchUniqueComplianceTypesQuery,
  useAddComplianceMutation,
  useUpdateComplianceMutation,
  useDeleteComplianceMutation,
} from "../store/api/cyberService/complianceAp";
import LinkCS from "../components/link/LinkCS";

const CSTLink = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isLinkModalVisible, setIsLinkModalVisible] = useState(false);
  const [editRecord, setEditRecord] = useState(null);
  const [linkRecord, setLinkRecord] = useState(null);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState(null);
  const [selectedScannerTypes, setSelectedScannerTypes] = useState([]);
  const [tableData, setTableData] = useState([]);

  const { data: complianceData, refetch: refetchComplianceData } = useFetchCompliancesQuery(activeTab);
  const { data: complianceTypes, isLoading: isLoadingTypes } = useFetchUniqueComplianceTypesQuery();
  const [addCompliance, { isLoading: isAdding }] = useAddComplianceMutation();
  const [updateCompliance, { isLoading: isUpdating }] = useUpdateComplianceMutation();
  const [deleteCompliance] = useDeleteComplianceMutation();

  const onFinish = async (values) => {
    const payload = {
      compliance_type: values.compliance_type,
      compliance_control_name: values.compliance_control_name,
      compliance_group_name: values.compliance_group_name,
      compliance_subset_name: values.compliance_subset_name,
    };

    try {
      if (editRecord) {
        await updateCompliance({ complianceId: editRecord._id, updatedData: payload }).unwrap();
        message.success("Compliance updated successfully!");
      } else {
        await addCompliance(payload).unwrap();
        message.success("Compliance added successfully!");
      }

      form.resetFields();
      setIsModalVisible(false);
    } catch (error) {
      message.error("Failed to submit compliance. Please try again.");
    }
  };
  
    const handleEdit = (record) => {
      setEditRecord(record);
      form.setFieldsValue({
        compliance_type: record.compliance_type,
        compliance_control_name: record.compliance_control_name,
        compliance_group_name: record.compliance_group_name,
        compliance_subset_name: record.compliance_subset_name,
      });
      setIsModalVisible(true);
      setLinkRecord(true)
    };

  useEffect(() => {
    if (!isLinkModalVisible) {
      refetchComplianceData(); 
    }
  }, [isLinkModalVisible, refetchComplianceData]);
  
  const tabItems = complianceTypes?.data
  ?.map((type) => ({
    label: type,
    key: type,
  })) || [];

  useEffect(() => {
    if (!activeTab && tabItems.length > 0) {
      setActiveTab(tabItems[1]?.key);
    }
  }, [complianceTypes, tabItems, activeTab]);

  const handleDelete = async (id) => {debugger
    try {
      await deleteCompliance(id).unwrap();
      message.success("Compliance deleted successfully!");
    } catch (error) {
      message.error(error?.data?.error || "Failed to delete compliance.");
    }
  };

  const handleAdd = () => {
    setEditRecord(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleLinkClick = (record) => {
    setLinkRecord(record);
    setIsLinkModalVisible(true);
  };

  const updateLinkedRecord = (updatedRecord) => {
    setTableData((prevData) =>
      prevData.map((item) =>
        item._id === updatedRecord._id ? { ...item, compliance_id: updatedRecord.scanner_types } : item
      )
    );
    setSelectedScannerTypes(updatedRecord.compliance_id?.map((s) => s.scan_type) || []);
    setIsLinkModalVisible(false);
    refetchComplianceData();
  };
  
  const filteredData = activeTab
    ? complianceData?.data?.filter((item) => item.compliance_type === activeTab) || []
    : complianceData?.data || [];
    const filteredRows = filteredData.filter((item) => {
      if (selectedScannerTypes.length === 0) {
        return true; 
      }
      return item.scanner_types?.some((scanner) =>
        selectedScannerTypes.includes(scanner?.scan_type)
      );
    });
    
  const columns = [
    { title: "Control Name", dataIndex: "compliance_control_name"},
    { title: "Group Name", dataIndex: "compliance_group_name" },
    // { title: "Sub-Set", dataIndex: "compliance_subset_name" },
    { title: "Actions",
        render: (_, record) => (
          <div style={{ display: "flex", gap: "8px" }}>
              <Button icon={<EditOutlined />} onClick={() => handleEdit(record)}  />
               <Button icon={<LinkOutlined />}onClick={() => handleLinkClick(record)}/>
            
            <Popconfirm title="Are you sure you want to delete this compliance?" onConfirm={() => handleDelete(record._id)}>
              <Button icon={<DeleteOutlined />} style={{ color: "red" }} />
            </Popconfirm>
          </div>
        ),
      },
    ];
    
  return (
    <ConfigProvider theme={{ token: { colorPrimary: "#6BE992" } }}>
      <div style={{ padding: "15px", marginTop: "20px" }}>
        <div style={{ fontSize: "20px", marginBottom: "20px" }}>Compliance-ScannerTypes</div>
         <div style={{display: "flex",justifyContent: "flex-end",marginBottom: "30px",}}>
                  <Button type="primary" onClick={handleAdd}>Add Compliance </Button>
                </div>
        {isLoadingTypes ? (
          <Spin tip="Loading compliance types..." />
        ) : (
          <Tabs
            activeKey={activeTab}
            onChange={(key) => setActiveTab(key)}
            items={tabItems}
            tabBarStyle={{ display: "flex",gap: "20px",paddingBottom: "10px",}}
          />
        )}
        <Table
          columns={columns}
          dataSource={filteredRows?.length ? [...filteredRows].reverse() : []}
          rowKey="_id"
          loading={!complianceData}
          pagination={false}
          bordered
          style={{ marginTop: "20px" }}
        />
      </div>
      <Modal
        title={editRecord ? "Edit Compliance" : "Add Compliance"}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
      <Form layout="vertical" form={form} onFinish={onFinish} initialValues={{}}>
      <Form.Item
            name="compliance_type" label="Compliance Type"
            rules={[{ required: true, message: "Please select the compliance type" },]}
          >
            <Select
              placeholder="Select compliance type"
              loading={isLoadingTypes}
              options={
                complianceTypes?.data
                  ?.filter((type) => type !== "")
                  .map((type) => ({
                    label: type,
                    value: type,
                  })) || []
              }
            />
          </Form.Item>
          <Form.Item
            name="compliance_control_name" label="Control Name"
            rules={[ { required: true, message: "Please enter the control name" },]}
          >
            <Input placeholder="Enter control name" />
          </Form.Item>
          <Form.Item
            name="compliance_group_name" label="Group Name"
            rules={[{ required: true, message: "Please enter the group name" },]}
          >
            <Input placeholder="Enter group name" />
          </Form.Item>
          <Form.Item
          name="compliance_subset_name"
          label="Subset"
          rules={[]}
        >
          <Input placeholder="Enter Subset (Optional)" />
        </Form.Item>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
          <Button onClick={() => setIsModalVisible(false)}>Cancel</Button>
          <Button type="primary" htmlType="submit" loading={isAdding || isUpdating}> Submit</Button>
        </div>
      </Form>
    </Modal>
      <Modal
        title="Link Compliance & Scanner Types"
        open={isLinkModalVisible}
        onCancel={() => setIsLinkModalVisible(false)}
        footer={null}
        width={900}
      >
        <Suspense fallback={<Spin tip="Loading LinkCS..." />}>
          <LinkCS
            record={linkRecord}
            selectedScannerTypes={selectedScannerTypes}
            setSelectedScannerTypes={setSelectedScannerTypes}
            updateLinkedRecord={updateLinkedRecord}
            refetchComplianceData={refetchComplianceData}
            onClose={() => setIsLinkModalVisible(false)}
            editRecord={editRecord}
          />
        </Suspense>
      </Modal>
    </ConfigProvider>
  );
};

export default CSTLink;
