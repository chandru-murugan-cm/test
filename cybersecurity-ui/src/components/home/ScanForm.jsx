import { Form, Input, Button } from "antd";

const ScanForm = ({ onFinish, loading, handleReset, form }) => {
  return (
    <div style={{ margin: "0 auto 20px" }}>
      <h2
        style={{
          textAlign: "left",
          marginBottom: "20px",
          fontSize: "24px",
          marginTop: 0,
          color: "#113032",
        }}
      >
        Add New Project
      </h2>
      <div style={{ maxWidth: "420px" }}>
        <Form
          form={form}
          name="basic"
          labelCol={{ span: 6 }}
          wrapperCol={{ span: 18 }}
          initialValues={{ remember: true }}
          onFinish={onFinish}
          layout="horizontal"
          style={{ marginBottom: "20px" }}
        >
          <Form.Item
            label="Project Name"
            name="projectName"
            rules={[
              { required: true, message: "Please input your project name!" },
            ]}
            style={{ marginBottom: "12px" }}
          >
            <Input placeholder="Enter your project name" />
          </Form.Item>
          <Form.Item
            label="Website URL"
            name="websiteUrl"
            rules={[
              { required: true, message: "Please input your website URL!" },
            ]}
            style={{ marginBottom: "12px" }}
          >
            <Input placeholder="Enter your website URL" />
          </Form.Item>

          <Form.Item
            label="GitHub URL"
            name="githubUrl"
            rules={[
              { required: true, message: "Please input your GitHub URL!" },
            ]}
            style={{ marginBottom: "12px" }}
          >
            <Input placeholder="Enter your GitHub URL" />
          </Form.Item>

          <Form.Item wrapperCol={{ offset: 6, span: 18 }}>
            <Button
              type="primary"
              color="default"
              variant="solid"
              htmlType="submit"
              loading={loading}
              style={{ marginRight: "10px", backgroundColor: "#6BE992" }}
            >
              Submit
            </Button>
            <Button type="default" onClick={handleReset}>
              Reset
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default ScanForm;
