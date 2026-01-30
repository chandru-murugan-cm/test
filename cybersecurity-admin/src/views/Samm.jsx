import React, { useState, useEffect, Suspense } from "react";
import { ConfigProvider, Table, Tabs, Button, Modal, Form, Input, Select, message, Popconfirm, Spin } from "antd";
import { DeleteOutlined, EditOutlined, LinkOutlined } from "@ant-design/icons";
import { useDeleteSammMutation, useUpdateSammMutation, useAddSammMutation, useFetchBusinessfunctionsQuery } from "../store/api/cyberService/sammApi";
import { useFetchFrameworkScannerTypeQuery } from "../store/api/cyberService/FrameworkScannerTypesApi";
import LinkFS from "../components/link/LinkFS";

const Samm = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editRecord, setEditRecord] = useState(null);
  const [activeTab, setActiveTab] = useState(null);
  const [form] = Form.useForm();
  const [isLinkModalVisible, setIsLinkModalVisible] = useState(false);
  const [tableData, setTableData] = useState([]);
  const [linkRecord, setLinkRecord] = useState(null);
  const [selectedScannerTypes, setSelectedScannerTypes] = useState([]);

  const { data: frameworksData, isLoading: isLoadingData, refetch: refetchframeworksData } = useFetchFrameworkScannerTypeQuery(activeTab);
  const { data: businessFunctionsData, isLoading: isLoadingTabs } = useFetchBusinessfunctionsQuery();
  const [updateFrameworks] = useUpdateSammMutation();
  const [addFrameworks] = useAddSammMutation();
  const [deleteFrameworks] = useDeleteSammMutation();
  
  useEffect(() => {
    if (businessFunctionsData?.data?.length > 0 && !activeTab) {setActiveTab(businessFunctionsData.data[0]);  }
  }, [businessFunctionsData, activeTab]);

  const filteredData = activeTab? frameworksData?.[0]?.data?.filter((item) => item?.l1_business_function === activeTab) || []: frameworksData?.data || [];
  const filteredRows = filteredData.filter((item) => {
    if (selectedScannerTypes.length === 0) {
      return true;
    }return item.scanner_types?.some((scanner) => selectedScannerTypes.includes(scanner?.scan_type));
  });

  const handleTabChange = (key) => {
    setActiveTab(key);
    refetchframeworksData();
  };

  const handleSubmit = async (values) => {
    const capitalizeFirstLetter = (str) => str.charAt(0).toUpperCase() + str.slice(1);
    const payload = {
      l1_business_function: capitalizeFirstLetter(values.l1_business_function),
      l2_security_practice: capitalizeFirstLetter(values.l2_security_practice),
      l3_stream: capitalizeFirstLetter(values.l3_stream),
      l4_strategy_and_metrics: capitalizeFirstLetter(values.l4_strategy_and_metrics),
      l4_strategy_and_metrics_description: capitalizeFirstLetter(values.l4_strategy_and_metrics_description),
      l4_strategy_and_metrics_question: capitalizeFirstLetter(values.l4_strategy_and_metrics_question),
      l4_strategy_and_metrics_coverage: values.l4_strategy_and_metrics_coverage.map((coverage) => ({
        ...coverage,
        coverage_name: capitalizeFirstLetter(coverage.coverage_name),
        coverage_description: capitalizeFirstLetter(coverage.coverage_description),
        coverage_score: parseFloat(coverage.coverage_score),
      })),};
    try {
      if (editRecord) {
        await updateFrameworks({
          sammId: editRecord._id,
          updatedData: payload,}).unwrap();
        message.success("Framework updated successfully!");
      } else {
        await addFrameworks(payload).unwrap();
        message.success("Framework added successfully!");
      }
      setIsModalVisible(false);
      refetchframeworksData();
    } catch (error) {
      message.error(error?.data?.error || "Failed to save framework. Please try again.");
    }
  };

  useEffect(() => {
    if (!isLinkModalVisible) {refetchframeworksData();}
  }, [isLinkModalVisible, refetchframeworksData]);

  const handleEdit = (record) => {
    setEditRecord(record);
    form.setFieldsValue({
      ...record,
      l4_strategy_and_metrics_coverage: record.l4_strategy_and_metrics_coverage.map((coverage, index) => ({
        ...coverage,
        coverage_name: `Coverage ${index + 1}`,
        coverage_score: coverage.coverage_score,
      })),
    });
    setIsModalVisible(true);
    setLinkRecord(true);
  };

  const handleAdd = () => {
    setEditRecord(null);
    form.resetFields();
    const coverageData = frameworksData?.data?.[0]?.l4_strategy_and_metrics_coverage || [];
    form.setFieldsValue({
      l4_strategy_and_metrics_coverage: coverageData.map((coverage) => ({
        coverage_name: coverage.coverage_name,
        coverage_score: coverage.coverage_score,
        coverage_description: coverage.coverage_description || "",
      })), }); setIsModalVisible(true);
  };

  const handleLinkClick = (record) => { setLinkRecord(record);setIsLinkModalVisible(true);};

  const updateLinkedRecord = (updatedRecord) => {
    setTableData((prevData) =>
      prevData.map((item) =>
        item._id === updatedRecord._id ? { ...item, framework_id: updatedRecord.scanner_types } : item
      )
    );
    setSelectedScannerTypes(updatedRecord.framework_id?.map((s) => s.scan_type) || []);
    setIsLinkModalVisible(false);
    refetchframeworksData();
  };

  const handleDelete = async (id) => {
    try { await deleteFrameworks(id).unwrap();message.success("Framework deleted successfully!");
      refetchframeworksData();
    } catch (error) {message.error(error?.data?.error || "Failed to delete framework. Please try again.");
    }
  };
  const tabItems = businessFunctionsData?.data?.map((type) => ({label: type, key: type, })) || [];

  const columns = [
    { title: "Security Practice", dataIndex: "l2_security_practice", width: "12%" },
    { title: "Stream", dataIndex: "l3_stream", width: "12%" },
    { title: "Strategy & Metrics", dataIndex: "l4_strategy_and_metrics", width: "15%" },
    { title: "Question", dataIndex: "l4_strategy_and_metrics_question", width: "20%" },
    { title: "Description",dataIndex: "l4_strategy_and_metrics_description",width: "20%",},
    { title: "Actions", width: "2%",render: (_, record) => (
        <div style={{ display: "flex", gap: "8px" }}>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button icon={<LinkOutlined />} onClick={() => handleLinkClick(record)} />
          <Popconfirm title="Are you sure you want to delete this Framework?" onConfirm={() => handleDelete(record._id)}>
            <Button icon={<DeleteOutlined />} style={{ color: "red" }} />
          </Popconfirm>
        </div>
      ),
    },
  ];

  return (
    <ConfigProvider theme={{ token: { colorPrimary: "#6BE992" } }}>
      <div style={{ padding: "15px", marginTop: "20px" }}>
        <div style={{ fontSize: "20px", marginBottom: "20px" }}>SAMM(Software Assurance Maturity Model)</div>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "10px",
          }}
        >
          <Button type="primary" onClick={handleAdd}>
            {" "}
            Add New 
          </Button>
        </div>
        <Tabs
          activeKey={activeTab}
          onChange={handleTabChange}
          items={tabItems}
        />
        {isLoadingData ? (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: "50vh",
            }}
          >
            <Spin size="large" />
          </div>
        ) : (
          <Table
            columns={columns}
            dataSource={filteredRows?.length ? [...filteredRows].reverse() : []}
            rowKey="id"
            pagination={false}
            bordered
            style={{ marginTop: "20px" }}
          />
        )}
      </div>
      <Modal
        title={editRecord ? "Edit Framework" : "Add Framework"}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form layout="vertical" form={form} onFinish={handleSubmit}>
          <Form.Item
            name="l1_business_function"
            label="Business Function"
            rules={[
              { required: true, message: "Please select a business function" },
            ]}
          >
            <Select>
              {tabItems.map((item) => (
                <Select.Option key={item.key} value={item.key}>
                  {" "}
                  {item.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="l2_security_practice"
            label="Security Practice"
            rules={[
              { required: true, message: "Please enter the security practice" },
            ]}
          >
            <Input placeholder="Enter security practice" />
          </Form.Item>
          <Form.Item
            name="l3_stream"
            label="Stream"
            rules={[{ required: true, message: "Please enter the stream" }]}
          >
            <Input placeholder="Enter stream" />
          </Form.Item>
          <Form.Item
            name="l4_strategy_and_metrics"
            label="Strategy and Metrics"
            rules={[
              { required: true, message: "Please enter strategy and metrics" },
            ]}
          >
            <Input placeholder="Enter strategy and metrics" />
          </Form.Item>
          <Form.List name="l4_strategy_and_metrics_coverage">
            {(fields) => (
              <>
                {fields.map(({ key, name, fieldKey }) => (
                  <div key={key} style={{ marginBottom: "10px" }}>
                    <Form.Item
                      name={[name, "coverage_name"]}
                      fieldKey={[fieldKey, "coverage_name"]}
                      label={`Coverage Name ${key + 1}`}
                    >
                      <Input value={fields[key]?.coverage_name} disabled />
                    </Form.Item>
                    <Form.Item
                      name={[name, "coverage_description"]}
                      fieldKey={[fieldKey, "coverage_description"]}
                      label="Coverage Description"
                      rules={[
                        {
                          required: true,
                          message: "Coverage Description is required",
                        },
                      ]}
                    >
                      <Input
                        placeholder="Enter coverage description"
                        defaultValue={fields[key]?.coverage_description}
                      />
                    </Form.Item>
                    <Form.Item
                      name={[name, "coverage_score"]}
                      fieldKey={[fieldKey, "coverage_score"]}
                      label="Coverage Score"
                    >
                      <Input value={fields[key]?.coverage_score} disabled />
                    </Form.Item>{" "}
                  </div>
                ))}{" "}
              </>
            )}
          </Form.List>
          <Form.Item
            name="l4_strategy_and_metrics_description"
            label="Strategy & Metrics Description"
            rules={[
              { required: true, message: "Please enter the description" },
            ]}
          >
            <Input.TextArea
              placeholder="Enter strategy & metrics description"
              rows={3}
            />
          </Form.Item>
          <Form.Item
            name="l4_strategy_and_metrics_question"
            label="Strategy & Metrics Question"
            rules={[{ required: true, message: "Please enter the question" }]}
          >
            <Input placeholder="Enter strategy & metrics question" />
          </Form.Item>
          <div
            style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}
          >
            <Button onClick={() => setIsModalVisible(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit">
              {" "}
              Submit
            </Button>
          </div>
        </Form>
      </Modal>
      <Modal
        title="Link Framework & Scanner Types"
        open={isLinkModalVisible}
        onCancel={() => setIsLinkModalVisible(false)}
        footer={null}
        width={900}
      >
        <Suspense fallback={<Spin tip="Loading LinkCS..." />}>
          <LinkFS
            record={linkRecord}
            selectedScannerTypes={selectedScannerTypes}
            setSelectedScannerTypes={setSelectedScannerTypes}
            updateLinkedRecord={updateLinkedRecord}
            refetchframeworksData={refetchframeworksData}
            onClose={() => setIsLinkModalVisible(false)}
            editRecord={editRecord}
          />
        </Suspense>
      </Modal>
    </ConfigProvider>
  );
};

export default Samm;
