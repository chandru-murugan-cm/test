import React, { useState } from "react";
import { Modal, Steps, Button, Form, Input, Typography, Upload, message, Tooltip } from "antd";
import { UploadOutlined, CopyOutlined } from "@ant-design/icons";

const { Step } = Steps;
const { Title, Text } = Typography;

const GcpConfiguration = ({ visible, onCancel, onFinish }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [form] = Form.useForm();
    const [fileList, setFileList] = useState([]);
    const [serviceAccountKeyUploaded, setServiceAccountKeyUploaded] = useState(false);
    const [jsonData, setJsonData] = useState(null); 
    const [cloudName, setCloudName] = useState("");

    const handleNext = () => {
        form.validateFields()
            .then((values) => {
                if (currentStep < steps.length - 1) {
                  if (currentStep === 0) {
                    setCloudName(values.cloudName); // Save cloud name
                  }
                    setCurrentStep(currentStep + 1);
                } else {
                    if (!serviceAccountKeyUploaded && currentStep === steps.length - 1) {
                        message.error("Please upload the Service Account Key JSON file.");
                        return;
                    }
                    onFinish({ serviceAccountKey: jsonData, cloudName: cloudName }); 
                }
            })
            .catch((info) => {
                console.log("Validate Failed:", info);
            });
    };

    const handlePrevious = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const handleCancel = () => {
      onCancel(); 
      setCurrentStep(0);
      form.resetFields(); 
    };

    const validateServiceAccountKey = (fileinfo) => {
        const file = fileinfo.fileList[0].originFileObj;
        const reader = new FileReader();

        reader.onload = (e) => {
            const fileContent = e.target.result;
            try {
                const jsonData = JSON.parse(fileContent);
                console.log("Parsed JSON Data:", jsonData);

                // Validate required fields
                const requiredFields = ['type', 'project_id', 'private_key_id', 'private_key',
                    'client_email', 'client_id', 'auth_uri', 'token_uri',
                    'auth_provider_x509_cert_url', 'client_x509_cert_url'];
                const missingFields = requiredFields.filter(field => !(field in jsonData));
                if (missingFields.length > 0) {
                    message.error(`Missing fields: ${missingFields.join(', ')}`);
                    setServiceAccountKeyUploaded(false);
                    setFileList([]);
                    return false;
                }

                message.success(`${file.name} uploaded successfully.`);
                setServiceAccountKeyUploaded(true);
                setJsonData(jsonData); 
            } catch (error) {
                console.error('Error parsing JSON:', error.message);
                message.error(`Error parsing JSON: ${error.message}`);
                setServiceAccountKeyUploaded(false);
                setFileList([]);
                return false;
            }
        };

        reader.readAsText(file);
        return false; 
    };

    const handleUploadChange = (info) => {
        if (info.file.name) {
            const file = info.fileList[0].originFileObj;
            if (file) {
                validateServiceAccountKey(info);
            } else {
                message.error("File object is missing after selection.");
                setServiceAccountKeyUploaded(false);
            }
        } else {
            setServiceAccountKeyUploaded(false);
        }
        setFileList(info.fileList);
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
            title: "Create Security Audit Role",
            content: (
                <div>
                    <Title level={4}>Create Security Audit Role</Title>
                    <Text>
                        Follow these steps to create a new security audit role in CloudShell:
                    </Text>
                    <ol>
                        <li>
                            Log into your Google Cloud console and click on the <strong>"Activate"</strong> button for Cloud Shell.
                        </li>
                        <li>
                            Create a new file called <code>cyberwacht-security-audit-role.yaml</code> by running the following command in Cloud Shell:
                            <br />
                            <pre style={{ backgroundColor: '#f4f4f4', padding: '10px', position: 'relative' }}>
                                nano cyberwacht-security-audit-role.yaml
                                <Tooltip title="Copy command">
                                    <Button
                                        type="text"
                                        icon={<CopyOutlined />}
                                        style={{ position: 'absolute', top: '5px', right: '5px' }}
                                        onClick={() => {
                                            navigator.clipboard.writeText('nano cyberwacht-security-audit-role.yaml');
                                            message.success('Command copied to clipboard!');
                                        }}
                                    />
                                </Tooltip>
                            </pre>
                        </li>
                        <li>
                            Copy and paste the following YAML code into the file:
                            <br />
                            <div style={{ position: 'relative', marginTop: 16, marginBottom: 16 }}>
                                <Input.TextArea
                                    value={
                                        `name: roles/CyberWachtSecurityAudit
title: CyberWacht Security Audit
includedPermissions:
  - cloudasset.assets.listResource
  - cloudkms.cryptoKeys.list
  - cloudkms.keyRings.list
  - cloudsql.instances.list
  - cloudsql.users.list
  - compute.autoscalers.list
  - compute.backendServices.list
  - compute.disks.list
  - compute.firewalls.list
  - compute.healthChecks.list
  - compute.instanceGroups.list
  - compute.instances.getIamPolicy
  - compute.instances.list
  - compute.networks.list
  - compute.projects.get
  - compute.securityPolicies.list
  - compute.subnetworks.list
  - compute.targetHttpProxies.list
  - container.clusters.list
  - dns.managedZones.list
  - iam.serviceAccountKeys.list
  - iam.serviceAccounts.list
  - logging.logMetrics.list
  - logging.sinks.list
  - monitoring.alertPolicies.list
  - resourcemanager.folders.get
  - resourcemanager.folders.getIamPolicy
  - resourcemanager.folders.list
  - resourcemanager.hierarchyNodes.listTagBindings
  - resourcemanager.organizations.get
  - resourcemanager.organizations.getIamPolicy
  - resourcemanager.projects.get
  - resourcemanager.projects.getIamPolicy
  - resourcemanager.projects.list
  - resourcemanager.resourceTagBindings.list
  - resourcemanager.tagKeys.get
  - resourcemanager.tagKeys.getIamPolicy
  - resourcemanager.tagKeys.list
  - resourcemanager.tagValues.get
  - resourcemanager.tagValues.getIamPolicy
  - resourcemanager.tagValues.list
  - storage.buckets.getIamPolicy
  - storage.buckets.list
  - deploymentmanager.deployments.list
  - dataproc.clusters.list
  - artifactregistry.repositories.list
  - composer.environments.list
stage: GA`
                                    }
                                    autoSize={{ minRows: 10, maxRows: 10 }}
                                    readOnly
                                    style={{ whiteSpace: 'pre-wrap', overflowY: 'scroll' }}
                                />
                                <Tooltip title="Copy YAML content">
                                    <Button
                                        type="text"
                                        icon={<CopyOutlined />}
                                        style={{ position: 'absolute', top: '5px', right: '5px' }}
                                        onClick={() => {
                                            navigator.clipboard.writeText(`name: roles/CyberWachtSecurityAudit
    title: CyberWacht Security Audit
    includedPermissions:
      - cloudasset.assets.listResource
      - cloudkms.cryptoKeys.list
      - cloudkms.keyRings.list
      - cloudsql.instances.list
      - cloudsql.users.list
      - compute.autoscalers.list
      - compute.backendServices.list
      - compute.disks.list
      - compute.firewalls.list
      - compute.healthChecks.list
      - compute.instanceGroups.list
      - compute.instances.getIamPolicy
      - compute.instances.list
      - compute.networks.list
      - compute.projects.get
      - compute.securityPolicies.list
      - compute.subnetworks.list
      - compute.targetHttpProxies.list
      - container.clusters.list
      - dns.managedZones.list
      - iam.serviceAccountKeys.list
      - iam.serviceAccounts.list
      - logging.logMetrics.list
      - logging.sinks.list
      - monitoring.alertPolicies.list
      - resourcemanager.folders.get
      - resourcemanager.folders.getIamPolicy
      - resourcemanager.folders.list
      - resourcemanager.hierarchyNodes.listTagBindings
      - resourcemanager.organizations.get
      - resourcemanager.organizations.getIamPolicy
      - resourcemanager.projects.get
      - resourcemanager.projects.getIamPolicy
      - resourcemanager.projects.list
      - resourcemanager.resourceTagBindings.list
      - resourcemanager.tagKeys.get
      - resourcemanager.tagKeys.getIamPolicy
      - resourcemanager.tagKeys.list
      - resourcemanager.tagValues.get
      - resourcemanager.tagValues.getIamPolicy
      - resourcemanager.tagValues.list
      - storage.buckets.getIamPolicy
      - storage.buckets.list
      - deploymentmanager.deployments.list
      - dataproc.clusters.list
      - artifactregistry.repositories.list
      - composer.environments.list
    stage: GA`);
                                            message.success('YAML file content copied to clipboard!');
                                        }}
                                    />
                                </Tooltip>
                            </div>
                            Copy and paste the following yaml code in the file on your Cloud Shell, press Ctrl + X and type "Y" to save the file.
                            <br /><strong>Note!</strong> Exclude all rows starting with 'resourcemanager' if you do not use Organization.
                        </li>
                        <li>
                            Run the following command to create the role, use your Organization Id to create the Role at the Org Level:
                            <br />
                            <div style={{ position: 'relative', marginTop: 16, marginBottom: 16 }}>
                                <Input.TextArea
                                    value={`gcloud iam roles create CyberWachtSecurityAudit --organization=YOUR_ORGANIZATION_ID --file=cyberwacht-security-audit-role.yaml`}
                                    autoSize={{ minRows: 2, maxRows: 2 }}
                                    readOnly
                                    style={{ whiteSpace: 'pre-wrap', overflowY: 'scroll' }}
                                />
                                <Tooltip title="Copy command">
                                    <Button
                                        type="text"
                                        icon={<CopyOutlined />}
                                        style={{ position: 'absolute', top: '5px', right: '5px' }}
                                        onClick={() => {
                                            navigator.clipboard.writeText(`gcloud iam roles create CyberWachtSecurityAudit --organization=YOUR_ORGANIZATION_ID --file=cyberwacht-security-audit-role.yaml`);
                                            message.success('Command copied to clipboard!');
                                        }}
                                    />
                                </Tooltip>
                            </div>
                            You can use <i>--project=YOUR_PROJECT_ID</i> instead of <i>--organization=YOUR_ORGANIZATION_ID</i>
                            <br />
                            <div style={{ position: 'relative', marginTop: 16, marginBottom: 16 }}>
                                <Input.TextArea
                                    value={`--project=YOUR_PROJECT_ID`}
                                    autoSize={{ minRows: 2, maxRows: 2 }}
                                    readOnly
                                    style={{ whiteSpace: 'pre-wrap', overflowY: 'scroll' }}
                                />
                                <Tooltip title="Copy command">
                                    <Button
                                        type="text"
                                        icon={<CopyOutlined />}
                                        style={{ position: 'absolute', top: '5px', right: '5px' }}
                                        onClick={() => {
                                            navigator.clipboard.writeText(`--project=YOUR_PROJECT_ID`);
                                            message.success('Command copied to clipboard!');
                                        }}
                                    />
                                </Tooltip>
                            </div>
                        </li>
                    </ol>
                </div>
            ),
        },
        {
            title: "Create Service Account",
            content: (
                <div>
                    <Title level={4}>Create Service Account</Title>
                    <Text>Follow the steps below to create a service account for CyberWacht:</Text>
                    <ol>
                        <li>
                            Log into your Google Cloud console and navigate to <strong>IAM Admin &gt; Service Accounts</strong>.
                        </li>
                        <li>
                            Click on <strong>Create Service Account</strong>.
                        </li>
                        <li>
                            Enter <strong>CyberWacht</strong> as the Service account name and <strong>CyberWacht API Access</strong> as the description.
                        </li>
                        <li>Click <strong>Continue</strong>.</li>
                        <li>Select the role: <strong>Custom &gt; CyberWacht Security Audit</strong>.</li>
                        <li>Click <strong>Continue</strong> and then click <strong>Create Key</strong>.</li>
                        <li>Leave the default JSON option selected and click <strong>Create</strong>.</li>
                        <li>
                            The key will be downloaded to your machine.
                        </li>
                        <li>
                            Upload the downloaded JSON file below:
                            <Upload
                                accept=".json"
                                fileList={fileList}
                                onChange={handleUploadChange}
                                beforeUpload={() => false}  // Prevent auto-upload
                            >
                                <Button icon={<UploadOutlined />}>
                                    Upload Service Account Key <span style={{ color: 'red' }}>*</span>
                                </Button>
                            </Upload>
                        </li>
                    </ol>
                </div>
            ),
        },
    ];

    return (
        <Modal
            title="Google Cloud Platform Configuration"
            visible={visible}
            onCancel={handleCancel}
            footer={[
                <Button key="back" onClick={handlePrevious} disabled={currentStep === 0}>
                    Previous
                </Button>,
                <Button key="next" type="primary" onClick={handleNext}>
                    {currentStep < steps.length - 1 ? "Save & Continue" : "Finish"}
                </Button>,
            ]}
        >
            <Steps current={currentStep} direction="vertical" style={{ marginTop: 24 }}>
                {steps.map((step, index) => (
                    <Step key={index} title={step.title} />
                ))}
            </Steps>
            <div className="steps-content" style={{ marginTop: 24 }}>
                {steps[currentStep].content}
            </div>
        </Modal>
    );
};

export default GcpConfiguration;
