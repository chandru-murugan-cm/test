import React, { useState } from "react";
import {
  Form,
  Input,
  Button,
  Upload,
  Typography,
  Card,
  Space,
  Select,
  message,
} from "antd";
import { UploadOutlined } from "@ant-design/icons";
import { useAddProjectMutation } from "../store/api/cyberService/projectApi";

const { Title } = Typography;
const { Option } = Select;

const AddProject = () => {
  const [form] = Form.useForm();
  const [addProject, { isLoading }] = useAddProjectMutation();
  const [authToken, setAuthToken] = useState(null);

  const onFinish = async (values) => {
    try {
      await addProject({
        name: values.projectName,
        domain_value: values.websiteUrl,
        repo_url: values.githubUrl,
        organization: "",
      }).unwrap();

      message.success("Project added successfully!");
    } catch (error) {
      message.error("Failed to add the project. Please try again.");
    }
  };
  console.log(authToken, "auth token");
  return (
    <Card
      style={{
        width: "100%",
        maxWidth: "550px",
        borderRadius: "8px",
        border: "none",
      }}
    >
      <Title level={4} style={{ marginBottom: "20px", color: "#113032" }}>
        Add New Project
      </Title>
      <Form
        form={form}
        name="addProject"
        labelCol={{ span: 8 }}
        wrapperCol={{ span: 16 }}
        onFinish={onFinish}
        layout="horizontal"
        labelAlign="left"
      >
        <Form.Item
          label="Project Name"
          name="projectName"
          rules={[
            { required: true, message: "Please input your project name!" },
          ]}
        >
          <Input placeholder="Enter project name" />
        </Form.Item>

        <Form.Item
          label="Website URL"
          name="websiteUrl"
          rules={[
            { required: true, message: "Please input your website URL!" },
          ]}
        >
          <Input placeholder="Enter website URL" />
        </Form.Item>

        <Form.Item
          label="GitHub URL"
          name="githubUrl"
          rules={[{ required: true, message: "Please input your GitHub URL!" }]}
        >
          <Input placeholder="Enter GitHub URL" />
        </Form.Item>

        <Form.Item label="Business Criticality" name="businessCriticality">
          <Select mode="multiple" placeholder="Select business criticality">
            <Option value="Very High">Very High</Option>
            <Option value="High">High</Option>
            <Option value="Medium">Medium</Option>
            <Option value="Low">Low</Option>
            <Option value="Very Low">Very Low</Option>
            <Option value="None">None</Option>
          </Select>
        </Form.Item>

        <Form.Item label="Platform" name="platform">
          <Select mode="multiple" placeholder="Select platform">
            <Option value="API">API</Option>
            <Option value="Desktop">Desktop</Option>
            <Option value="IoT">Internet of Things</Option>
            <Option value="Mobile">Mobile</Option>
            <Option value="Web">Web</Option>
          </Select>
        </Form.Item>

        <Form.Item label="Lifecycle" name="lifecycle">
          <Select mode="multiple" placeholder="Select lifecycle">
            <Option value="Production">Production</Option>
            <Option value="Staging">Staging</Option>
            <Option value="Development">Development</Option>
          </Select>
        </Form.Item>

        <Form.Item label="Docker File" name="dockerFile">
          <Upload beforeUpload={() => false}>
            <Button icon={<UploadOutlined />}>Upload Docker File</Button>
          </Upload>
        </Form.Item>

        <Form.Item label="Kubernetes File" name="kubernetesFile">
          <Upload beforeUpload={() => false}>
            <Button icon={<UploadOutlined />}>Upload Kubernetes File</Button>
          </Upload>
        </Form.Item>

        <Form.Item wrapperCol={{ offset: 8, span: 16 }}>
          <Button
            type="primary"
            htmlType="submit"
            loading={isLoading}
            style={{ background: "#6BE992", boxShadow: "none" }}
          >
            Submit
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default AddProject;
