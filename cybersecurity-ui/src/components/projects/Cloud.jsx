import React, { useState, useEffect } from "react";
import { Button, Modal, Form, Input, Steps, message, Progress, Select, Table, Tooltip, Typography, Collapse } from "antd";
import azureLogo from "../../assets/images/microsoft-azure.svg";
import gcpLogo from "../../assets/images/google_cloud-icon.svg";
import { EditOutlined, DeleteOutlined, PlusOutlined, EyeOutlined, EyeInvisibleOutlined } from "@ant-design/icons";
import { useAddCloudAzureMutation, useDeleteCloudAzureMutation } from "../../store/api/cyberService/cloudAzureApi";
import { useCheckFindingsBulkQuery } from "../../store/api/cyberService/scannerApi";
import ScanTypeTable from "./ScanTypeTable";
import GcpConfiguration from "./GcpConfiguration";
import { useAddCloudGoogleMutation, useDeleteCloudGoogleMutation } from "../../store/api/cyberService/cloudGoogleApi";

const { Step } = Steps;
const { Text, Title } = Typography;
const { Panel } = Collapse;

const CloudTab = ({projectDetails, refetch }) => {
    const [addCloudAzure, { isLoading: isAdding }] = useAddCloudAzureMutation();
    const [deleteCloudAzure, { isLoading: isdeletingAzure }] = useDeleteCloudAzureMutation();
    const [deleteCloudGoogle, { isLoading: isdeletingGoogle }] = useDeleteCloudGoogleMutation();
    const [addCloudGoogle, { isLoading: isAddingGoogle }] = useAddCloudGoogleMutation();
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);
    const [form] = Form.useForm();
    const [formValues, setFormValues] = useState({});
    const [visibleIds, setVisibleIds] = useState({});

    const [azureCloudDetails, setAzureCloudDetails] = useState([]);
    const [googleCloudDetails, setGoogleCloudDetails] = useState([]);
    const [selectedAzureCloud, setSelectedAzureCloud] = useState(null);
    const [isAddAzureModalVisible, setIsAddAzureModalVisible] = useState(false);
    const [isAddGcpModalVisible, setIsAddGcpModalVisible] = useState(false);

  const targetIds =
    projectDetails?.azure_cloud_data?.map((repo) => repo._id) || [];
  const { data, error, isLoading } = useCheckFindingsBulkQuery(targetIds, {
    skip: !targetIds || targetIds.length === 0,
  });

    useEffect(() => {
        if (projectDetails) {
            setAzureCloudDetails(
                projectDetails.azure_cloud_data ? projectDetails.azure_cloud_data : []
            );
            setGoogleCloudDetails(
                projectDetails.google_cloud_data ? projectDetails.google_cloud_data : []
            );
        }
    }, [projectDetails]);

    const isAddCloudButtonDisabled = azureCloudDetails.length > 0 && googleCloudDetails.length > 0;

    const isAzureDisabled = azureCloudDetails.length > 0;
    const isGoogleCloudDisabled = googleCloudDetails.length > 0;

  const toggleVisibility = (idType, recordId) => {
    setVisibleIds((prev) => ({
      ...prev,
      [recordId]: {
        ...prev[recordId],
        [idType]: !prev[recordId]?.[idType], // Toggle visibility
      },
    }));
  };

  const showAzureDeleteConfirm = (record) => {
    Modal.confirm({
        title: 'Are you sure you want to delete this Azure cloud configuration?',
        content: 'This action will permanently delete all findings related to this resource. This operation cannot be undone.',
        okText: 'Yes, delete',
        okType: 'danger',
        cancelText: 'Cancel',
        onOk() {
            handleAzureDelete(record);
        },
    });
};

  const handleAzureDelete = (record) => {
    console.log("Azure Record to Delete:", record);
    const azure_id = record?._id;
  
    // Call the deleteCloudAzure mutation
    deleteCloudAzure(azure_id)
      .unwrap()
      .then((response) => {
        message.success("Azure cloud configuration deleted successfully!");
        refetch(); // Refetch data to update the UI
      })
      .catch((error) => {
        console.error("Failed to delete Azure cloud configuration:", error);
        message.error("Failed to delete Azure cloud configuration. Please try again.");
      });
  };

  const showGoogleDeleteConfirm = (record) => {
    Modal.confirm({
        title: 'Are you sure you want to delete this Google cloud configuration?',
        content: 'This action will permanently delete all findings related to this resource. This operation cannot be undone.',
        okText: 'Yes, delete',
        okType: 'danger',
        cancelText: 'Cancel',
        onOk() {
            handleGoogleDelete(record);
        },
    });
};

  const handleGoogleDelete = (record) => {
    console.log("Google Record to Delete:", record);
    const google_id = record?._id;
  
    // Call the deleteCloudAzure mutation
    deleteCloudGoogle(google_id)
      .unwrap()
      .then((response) => {
        message.success("Azure cloud configuration deleted successfully!");
        refetch(); // Refetch data to update the UI
      })
      .catch((error) => {
        console.error("Failed to delete Google cloud configuration:", error);
        message.error("Failed to delete Google cloud configuration. Please try again.");
      });
  };
  

    const AzureCloudColumns = [
        {
          title: "Azure Cloud Name",
          dataIndex: "name",
          key: "name",
          width: "20%",
        },
        {
            title: "Application ID",
            dataIndex: "application_id",
            key: "application_id",
            width: "20%",
            render: (text, record) => (
                <div>
                    {visibleIds[record._id]?.application_id ? text : '****-****-****-****'}
                    <Tooltip>
                        <Button
                            icon={visibleIds[record._id]?.application_id ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                            onClick={() => toggleVisibility('application_id', record._id)}
                            type="link"
                        />
                    </Tooltip>
                </div>
            ),
        },
        {
            title: "Directory ID",
            dataIndex: "directory_id",
            key: "directory_id",
            width: "20%",
            render: (text, record) => (
                <div>
                    {visibleIds[record._id]?.directory_id ? text : '****-****-****-****'}
                    <Tooltip>
                        <Button
                            icon={visibleIds[record._id]?.directory_id ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                            onClick={() => toggleVisibility('directory_id', record._id)}
                            type="link"
                        />
                    </Tooltip>
                </div>
            ),
        },
        {
            title: "Subscription ID",
            dataIndex: "subscription_id",
            key: "subscription_id",
            width: "20%",
            render: (text, record) => (
                <div>
                    {visibleIds[record._id]?.subscription_id ? text : '****-****-****-****'}
                    <Tooltip>
                        <Button
                            icon={visibleIds[record._id]?.subscription_id ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                            onClick={() => toggleVisibility('subscription_id', record._id)}
                            type="link"
                        />
                    </Tooltip>
                </div>
            ),
        },
        {
          title: "Actions",
          key: "actions",
          render: (_, record) => (
            <div style={{ display: "flex", gap: "8px" }}>
              <Tooltip title="Edit">
                <Button
                  icon={<EditOutlined />}
                  type="link"
                //   disabled={data?.[record?._id]}
                  disabled
                  onClick={() => handleEdit(record)}
                />
              </Tooltip>
              <Tooltip title="Remove">
                <Button
                  icon={<DeleteOutlined />}
                  type="link"
                  danger
                  onClick={() => showAzureDeleteConfirm(record)}
                  // disabled
                />
              </Tooltip>
            </div>
          ),
        },
      ];

    const GoogleCloudColumns = [
        {
          title: "GCP Cloud Name",
          dataIndex: "name",
          key: "name",
          width: "20%",
        },
        {
          title: "GCP Project ID",
          dataIndex: "gcp_project_id",
          key: "gcp_project_id",
          width: "20%",
        },
        {
          title: "Type",
          dataIndex: "type",
          key: "type",
          width: "20%",
        },
        {
          title: "Email",
          dataIndex: "client_email",
          key: "client_email",
          width: "40%",
        },
        {
          title: "Actions",
          key: "actions",
          render: (_, record) => (
            <div style={{ display: "flex", gap: "8px" }}>
              <Tooltip title="Edit">
                <Button
                  icon={<EditOutlined />}
                  type="link"
                //   disabled={data?.[record?._id]}
                  disabled
                  onClick={() => handleEdit(record)}
                />
              </Tooltip>
              <Tooltip title="Remove">
                <Button
                  icon={<DeleteOutlined />}
                  type="link"
                  danger
                  onClick={() => showGoogleDeleteConfirm(record)}
                  // disabled
                />
              </Tooltip>
            </div>
          ),
        },
      ];
    
      const handleEdit = (record) => {
        setSelectedAzureCloud(record);
        form.setFieldsValue({
          domain_url: record.domain_url,
          domain_label: record.domain_label,
        });
        setIsAddAzureModalVisible(true);
      };

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setCurrentStep(0); // Reset to the first step
    setFormValues({}); // Clear form values
  };

  const handleNext = () => {
    form
      .validateFields()
      .then((values) => {
        // Merge current form values with accumulated values
        const updatedValues = { ...formValues, ...values };
        setFormValues(updatedValues);

        const newPayload = {
          project_id: projectDetails?._id,
          application_id: updatedValues.applicationId,
          directory_id: updatedValues.directoryId,
          client_secret_key: updatedValues.secretKey,
          subscription_id: updatedValues.subscriptionId,
          name: updatedValues.cloudName,
        };

        console.log("payload", newPayload);

        if (currentStep < steps.length - 1) {
          setCurrentStep(currentStep + 1);
        } else {
          // Final step, send API request
          addCloudAzure(newPayload)
            .unwrap()
            .then((response) => {
              message.success("Cloud configuration added successfully!");
              setIsModalVisible(false);
              setCurrentStep(0); // Reset the step after success
              refetch();
              form.resetFields();
              setIsAddAzureModalVisible(false);
            })
            .catch((error) => {
              // Extract the error message from the backend response
              const errorMessage = error?.error || "Failed to add cloud configuration. Please try again.";
              message.error(errorMessage);
              console.error("API error: ", error);
            });
        }
      })
      .catch((info) => {
        console.log("Validate Failed:", info);
        message.error("Please fill in the required fields.");
      });
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

    const steps = [
        {
            title: "Name your connection",
            content: (
                <div>
                    <Form form={form} layout="vertical">
                        <Form.Item
                            label="Name your Cloud"
                            name="cloudName"
                            rules={[{ required: true, message: "Please name your cloud!" }]}
                        >
                            <Input placeholder="Enter the cloud name" />
                        </Form.Item>
                    </Form>
                </div>
            ),
        },
        {
            title: "Register your app",
            content: (
                <>
                    <p>
                        <strong>Microsoft Azure Cloud Provider Configuration</strong>
                    </p>
                    <p>
                        <ol>
                            <li>Log into your <a href="https://portal.azure.com" target="_blank" rel="noopener noreferrer">Azure Portal</a> and navigate to the Microsoft Entra ID service.</li>
                            <li>Select App registrations and then click on <strong>New registration</strong>.</li>
                            <li>Enter "CyberWacht" and/or a descriptive name in the Name field, take note of it, it will be used again in step 3.</li>
                            <li>Leave the "Supported account types" default: "Accounts in this organizational directory only".</li>
                            <li>Click on <strong>Register</strong>.</li>
                        </ol>
                    </p>
                    <Form form={form} layout="vertical">
                        <Form.Item
                            label="Copy the Application ID and Paste it below."
                            name="applicationId"
                            rules={[{ required: true, message: "Please input the Application ID!" }]}
                        >
                            <Input placeholder="e3f65423-d5f6-41f3-b83a-4ab4298de7b" />
                        </Form.Item>
                        <Form.Item
                            label="Copy the Directory ID and Paste it below."
                            name="directoryId"
                            rules={[{ required: true, message: "Please input the Directory ID!" }]}
                        >
                            <Input placeholder="c40a0ba68-d324-5912-baf8-7a8939fa9418" />
                        </Form.Item>
                    </Form>
                </>
            ),
        },
        {
            title: "Add a new secret",
            content: (
                <>
                    <p>
                        Now we need to add a secret and set an expiration date.
                    </p>
                    <ol>
                        <li>Click on <strong>Certificates & secrets</strong>.</li>
                        <li>Under <strong>Client secrets</strong>, click on <strong>New client secret</strong>.</li>
                        <li>Enter a Description (i.e., <em>CyberWacht</em>) and select Expires <strong>"In 2 years"</strong>.</li>
                        <li>Click on <strong>Add</strong>.</li>
                        <li>Copy the secret key value.</li>
                        <li>Paste the secret key value below.</li>
                    </ol>
                    <Form form={form} layout="vertical">
                        <Form.Item
                            label="Secret Key"
                            name="secretKey"
                            rules={[{ required: true, message: "Please input the Secret Key!" }]}
                        >
                            <Input.Password placeholder="Enter your secret key" />
                        </Form.Item>
                    </Form>
                </>
            ),
        },
        {
            title: "Add subscription",
            content: (
                <>
                    <p>
                        <strong>Subscriptions</strong>
                    </p>
                    <p>Navigate to Subscriptions and Connect your Subscription ID.</p>
                    <p>
                        Click on the relevant Subscription ID, copy and paste the ID below.
                    </p>
                    <Form form={form} layout="vertical">
                        <Form.Item
                            label="Subscription ID"
                            name="subscriptionId"
                            rules={[{ required: true, message: "Please input the Subscription ID!" }]}
                        >
                            <Input placeholder="Enter your subscription ID" />
                        </Form.Item>
                    </Form>

                </>
            ),
        },
        {
            title: "Grant access to roles",
            content: (
                <>
                    <p>
                        <strong>Grant access to roles</strong>
                    </p>
                    <p>
                        This is the final step, let's grant access to the roles we need.
                    </p>
                    <p>
                        <ol>
                            <li>Click on <strong>Access Control (IAM)</strong>.</li>
                            <li>Go to the <strong>Role assignments</strong> tab.</li>
                            <li>Click on <strong>Add</strong>, then <strong>Add role assignment</strong>.</li>
                            <li>In the "Role" list, search and select <strong>Security Reader</strong>.</li>
                            <li>Click <strong>Next</strong>.</li>
                            <li>Leave the "Assign access to" default value.</li>
                            <li>Click on <strong>Select Members</strong>, search for the name of the app registration (e.g., "CyberWacht") you created, and select it.</li>
                            <li>Click <strong>Select</strong>.</li>
                            <li>Click <strong>Review + Assign</strong>.</li>
                            <li>Repeat the process for the role <strong>Log Analytics Reader</strong>.</li>
                        </ol>
                    </p>
                </>
            ),
        }
    ];

    const handleGcpFinish = (values) => {
        console.log("GCP Configuration:", values);
        const serviceAccountKey= values.serviceAccountKey;
        const cloudName= values.cloudName;
        console.log("serviceAccountKey", serviceAccountKey);
        // Prepare the payload for the API call
        const payload = {
            project_id: projectDetails?._id,
            cloud_name: cloudName,
            auth_provider_x509_cert_url: serviceAccountKey?.auth_provider_x509_cert_url, 
            auth_uri: serviceAccountKey?.auth_uri,
            client_email: serviceAccountKey?.client_email,
            client_id: serviceAccountKey?.client_id,
            client_x509_cert_url: serviceAccountKey?.client_x509_cert_url,
            private_key: serviceAccountKey?.private_key,
            private_key_id: serviceAccountKey?.private_key_id,
            gcp_project_id: serviceAccountKey?.project_id,
            token_uri: serviceAccountKey?.token_uri,
            type: serviceAccountKey?.type,
            universe_domain: serviceAccountKey?.universe_domain,
        };
    
        // Call the addCloudGoogle mutation
        addCloudGoogle(payload)
            .unwrap()
            .then((response) => {
                message.success("GCP configuration added successfully!");
                setIsAddGcpModalVisible(false); // Close the modal
                refetch(); // Refetch the data to update the UI
            })
            .catch((error) => {
                console.error("Failed to add GCP configuration:", error);
                message.error("Failed to add GCP configuration. Please try again.");
            });
    };

  return (
    <div style={{ padding: "0px", borderRadius: "8px" }}>
      <div style={{ textAlign: "right", marginBottom: "16px" }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setSelectedAzureCloud(null);
            form.resetFields();
            setIsAddAzureModalVisible(true);
          }}
          loading={isAdding}
          style={{ background: "#6BE992", boxShadow: "none" }}
          disabled={isAddCloudButtonDisabled}
        >
          Add Cloud
        </Button>
      </div>
      <Collapse defaultActiveKey={['1']}>
        <Panel header="Azure Cloud Configurations" key="1">
          <Table
            dataSource={azureCloudDetails}
            columns={AzureCloudColumns}
            rowKey="_id"
            pagination={false}
            style={{ marginTop: "16px" }}
            bordered
          />
        </Panel>

        <Panel header="Google Cloud Configurations" key="2">
          <Table
            dataSource={googleCloudDetails}
            columns={GoogleCloudColumns}
            rowKey="_id"
            pagination={false}
            style={{ marginTop: "16px" }}
            bordered
          />
        </Panel>
      </Collapse>

      <ScanTypeTable targetTypes={["cloud"]} pagination={true} />

      <Modal
        title="Microsoft Azure Cloud Configuration"
        visible={isModalVisible}
        onCancel={handleCancel}
        footer={[
          <Button
            key="back"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            Previous
          </Button>,
          <Button
            key="next"
            type="primary"
            onClick={handleNext}
            loading={isAdding}
          >
            {currentStep < steps.length - 1 ? "Continue" : "Finish"}
          </Button>,
        ]}
      >
        <Progress percent={(currentStep / steps.length) * 100} />
        <Steps
          current={currentStep}
          direction="vertical"
          style={{ marginTop: 24 }}
        >
          {steps.map((step, index) => (
            <Step key={index} title={step.title} />
          ))}
        </Steps>
        <div className="steps-content" style={{ marginTop: 24 }}>
          {steps[currentStep].content}
        </div>
      </Modal>

                  {/* Add/Edit Cloud Modal */}
            <Modal
                visible={isAddAzureModalVisible}
                onCancel={() => setIsAddAzureModalVisible(false)}
                footer={null}
                bodyStyle={{ padding: '24px' }}
                centered
            >

                <Title level={4} style={{ textAlign: 'center' }}>Choose your cloud provider</Title>
                <Text style={{ display: 'block', textAlign: 'center', marginBottom: '24px' }}>
                    To get started, select the cloud platform you wish to link. We will guide you step by step through the process.
                </Text>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>


                    <Button
                        type="primary"
                        onClick={() => {
                            setIsAddGcpModalVisible(true);
                        }}
                        icon={<img src={gcpLogo} alt="Azure Logo" style={{ width: 20, marginRight: 8 }} />}
                        size="large"
                        style={{ border: 'none' }}
                        block
                        disabled={isGoogleCloudDisabled}
                    >
                        Google Cloud Platform
                    </Button>

                    <Button
                        type="primary"
                        onClick={showModal}
                        icon={<img src={azureLogo} alt="Azure Logo" style={{ width: 20, marginRight: 8 }} />}                        
                        size="large"
                        style={{ border: 'none' }}
                        block
                        disabled={isAzureDisabled}
                    >
                        Microsoft Azure Cloud
                    </Button>
                </div>

            </Modal>

            {/* GCP Configuration Modal */}
            <GcpConfiguration
                visible={isAddGcpModalVisible}
                onCancel={() => setIsAddGcpModalVisible(false)}
                onFinish={handleGcpFinish}
            />
        </div>
    );
};

export default CloudTab;
