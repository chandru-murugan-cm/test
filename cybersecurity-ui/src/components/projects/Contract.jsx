import React, { useEffect, useState } from "react";
import {
  Button,
  Modal,
  Input,
  Typography,
  message,
  Form,
  Upload,
  Table,
  Tooltip,
  Row,
  Col,
  Tabs,
} from "antd";
import {
  PlusOutlined,
  UploadOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined
} from "@ant-design/icons";
import { useDispatch } from "react-redux";
import {
  useAddContractMutation,
  useUpdateContractMutation,
  useDeleteContractMutation,
} from "../../store/api/cyberService/contractApi";
import ScanTypeTable from "./ScanTypeTable";

const { Text, Title } = Typography;
const { TabPane } = Tabs;
const { confirm } = Modal;

const ContractTab = ({ projectDetails, refetch }) => {
  const [isAddContractModalVisible, setIsAddContractModalVisible] = useState(false);
  const [uploadedSolFiles, setUploadedSolFiles] = useState([]);
  const [contractDetails, setContractDetails] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState(null);
  const [form] = Form.useForm();
  const [isDeleting, setIsDeleting] = useState(false); 
  const [addContract, { isLoading: isAdding }] = useAddContractMutation();
  const [updateContract] = useUpdateContractMutation();
  const [deleteContract] = useDeleteContractMutation();
  const dispatch = useDispatch();

  const handleSolFileUpload = (file) => {
    const isZip = file.type === "application/zip";
    const isSol = file.name.endsWith(".sol");
  
    // Check if a file has already been uploaded
    if (uploadedSolFiles.length > 0) {
      message.error("You can only upload either a .sol file or a .zip file, not both.");
      return Upload.LIST_IGNORE; // Prevent upload
    }
  
    // Allow only .sol or .zip files
    if (isZip || isSol) {
      debugger
      setUploadedSolFiles((prevFiles) => [...prevFiles, file]); // Add file to the list
      return false; // Prevent automatic upload
    } else {
      debugger
      message.error("You can only upload .sol or .zip files.");
      return Upload.LIST_IGNORE; // Prevent upload
    }
  };  

  const handleRemoveSolFile = (file) => {
    setUploadedSolFiles((prevFiles) => prevFiles.filter((f) => f.uid !== file.uid));
  };

  const handleAddOrEditContract = async (values) => {
    try {
      const { contractLabel, contractURL } = values;
      const uploadData = new FormData();

      // Add project ID
      uploadData.set("project_id", projectDetails?._id);

      // Add contract label and URL
      uploadData.set("contract_label", contractLabel);
      uploadData.set("contract_url", contractURL);

      // Add .sol files
      if (uploadedSolFiles.length === 0) {
        message.error("Please upload at least one .sol file.");
        return;
      }

      uploadedSolFiles.forEach((file) => {
        uploadData.append("files", file);
      });

      if (selectedBranch) {
        // Update existing contract
        await updateContract({
          id: selectedBranch,
          contractData: uploadData,
        });
        message.success("Contract updated successfully.");
      } else {
        // Add new contract
        await addContract(uploadData);
        message.success("Contract added successfully.");
      }

      setIsAddContractModalVisible(false);
      form.resetFields();
      setUploadedSolFiles([]);
      setSelectedBranch(null);
      refetch();
    } catch (error) {
      console.error("Error during contract upload:", error);
      message.error("Failed to upload files or update contract.");
    }
  };

  const handleEdit = (record) => {
    setSelectedBranch(record);
    form.setFieldsValue({
      contract_url: record.contract_url,
      contract_label: record.contract_label,
    });
    setIsAddContractModalVisible(true);
  };

  const handleDelete = async (record) => {
    setSelectedBranch(record);
    await deleteContract(record?._id);
    message.success("Contract deleted successfully.");
  };

  const showSmartContractDeleteConfirm = (record) => {
    confirm({
      title: (
        <>
          <ExclamationCircleOutlined style={{ color: 'red', marginRight: '8px' }} />
          Are you sure you want to delete this web3 configuration?
        </>
      ),
      content: (
        <div style={{ marginTop: '16px' }}>
          <p>
            Deleting this web3 will permanently remove all findings related to this resource.
          </p>
        </div>
      ),
      okText: 'Yes, delete',
      okType: 'danger',
      cancelText: 'Cancel',
      centered: true,
      icon: null,
      onOk() {
        handleSmartContractDelete(record);
      },
    });
  };

  const handleSmartContractDelete = (record) => {
    console.log("Smart Contract Record to Delete:", record);
    const contract_id = record?._id;

    setIsDeleting(true);

    deleteContract(contract_id)
      .unwrap()
      .then((response) => {
        message.success("Web3 configuration deleted successfully!");
        refetch();
      })
      .catch((error) => {
        console.error("Failed to delete Web3 configuration:", error);
        message.error("Failed to delete Web3 configuration. Please try again.");
      })
      .finally(() => {
        setIsDeleting(false);
      });
  };

  const contractColumns = [
    {
      title: "Contract Label",
      dataIndex: "contract_label",
      key: "contract_label",
      width: "20%",
    },
    {
      title: "Contract URL",
      dataIndex: "contract_url",
      key: "contract_url",
      width: "40%",
      render: (text) => (text !== "undefined" && text !== null && text !== "" ? text : "-"),
    },    
    {
      title: "Uploaded Files",
      key: "uploaded_files",
      width: "30%",
      render: (_, record) => {
        // Extract file names from solidity_files array and join with commas
        const fileNames = record.solidity_files
          ? record.solidity_files.map((file) => file.file_name).join(", ")
          : "N/A";
        return <span>{fileNames}</span>;
      },
    },
    {
      title: "Actions",
      key: "actions",
      width: "10%",
      render: (_, record) => (
        <div style={{ display: "flex", gap: "8px" }}>
          {/* <Tooltip title="Edit">
            <Button
              icon={<EditOutlined />}
              type="link"
              onClick={() => handleEdit(record)}
            />
          </Tooltip> */}
          <Tooltip title="Delete">
            <Button
              icon={<DeleteOutlined />}
              type="link"
              danger
              onClick={() => showSmartContractDeleteConfirm(record)}
              loading={isDeleting}
            />
          </Tooltip>
        </div>
      ),
    },
  ];

  useEffect(() => {
    if (projectDetails) {
      setContractDetails(
        projectDetails.contract_data ? projectDetails.contract_data : []
      );
    }
  }, [projectDetails]);

  const normFile = (e) => {
    if (Array.isArray(e)) {
      return e;
    }
    return e && e.fileList;
  };  

  return (
    <div style={{ padding: "16px" }}>
      <div style={{ textAlign: "right", marginBottom: "16px" }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setSelectedBranch(null);
            form.resetFields();
            setIsAddContractModalVisible(true);
          }}
          loading={isAdding}
          style={{ background: "#6BE992", boxShadow: "none" }}
          disabled={projectDetails?.contract_data?.length === 1}
        >
          Add Contracts
        </Button>
      </div>

      <Table
        dataSource={contractDetails}
        columns={contractColumns}
        rowKey="_id"
        pagination={false}
        style={{ marginTop: "16px" }}
        bordered
      />
      <ScanTypeTable targetTypes={["web3"]} pagination={true} />

      {/* Add/Edit Contract Modal */}
      <Modal
        visible={isAddContractModalVisible}
        onCancel={() => setIsAddContractModalVisible(false)}
        footer={null}
        bodyStyle={{ padding: "16px" }}
      >
        <Tabs defaultActiveKey="1">
          <TabPane tab="File Upload" key="1">
            <Form
              layout="vertical"
              onFinish={handleAddOrEditContract} // Submit handler for form submission
            >
              <Form.Item
                label="Contract Label"
                name="contractLabel"
                rules={[
                  { required: true, message: "Please enter a contract label" },
                ]}
              >
                <Input placeholder="Enter Contract Label" />
              </Form.Item>

              <Typography.Title level={4}>File Upload</Typography.Title>
              <Text>
                Upload your contract files. If you are uploading a single .sol file, it will be uploaded directly. If you have multiple .sol files, please upload them as a .zip file.
              </Text>
              <Row gutter={16} style={{ marginTop: "16px" }}>
                <Col span={12}>
                  <Form.Item
                    name="uploadedFile"
                    valuePropName="fileList"
                    getValueFromEvent={normFile}
                    rules={[
                      {
                        required: true,
                        message: "Please upload a .sol or .zip file",
                      },
                    ]}
                  >
                    <Upload
                      beforeUpload={handleSolFileUpload}
                      fileList={uploadedSolFiles}
                      showUploadList={{ showRemoveIcon: true }}
                      onRemove={handleRemoveSolFile}
                      multiple={false}
                      accept=".sol,.zip"
                    >
                      <Button icon={<UploadOutlined />}>Upload .sol Files or .zip</Button>
                    </Upload>
                  </Form.Item>
                </Col>
              </Row>
              <Button
                type="primary"
                htmlType="submit"
                style={{
                  width: "100%",
                  background: "#6BE992",
                  boxShadow: "none",
                  marginTop: "16px",
                }}
              >
                Add Contract Files
              </Button>
            </Form>
          </TabPane>
          <TabPane 
            tab={
              <span style={{ color: "rgba(0, 0, 0, 0.25)", cursor: "not-allowed" }}>
                GitHub Repository
              </span>
            } 
            key="2"
            disabled
          >
            <Typography.Title level={4}>GitHub Repository</Typography.Title>
            <Form
              layout="vertical"
              style={{ marginTop: "16px" }}
              onFinish={handleAddOrEditContract}
              form={form}
              initialValues={{
                contractUrl: projectDetails?.repo_url_data[0]?.repository_url,
                contractLabel: projectDetails?.repo_url_data[0]?.repository_label
              }}
            >
              <Form.Item label="Contract URL" name="contractUrl">
                <Input 
                  disabled 
                />
              </Form.Item>
              <Form.Item label="Contract Label" name="contractLabel">
                <Input 
                  disabled 
                />
              </Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                style={{ width: "100%", boxShadow: "none" }}
                // style={{ width: "100%", background: "#6BE992", boxShadow: "none" }}
                disabled
              >
                {selectedBranch ? "Update Contract" : "Start Scan"}
              </Button>
            </Form>
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  );
};

export default ContractTab;
