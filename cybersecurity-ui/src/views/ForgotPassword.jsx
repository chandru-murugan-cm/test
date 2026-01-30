import React, { useState } from "react";
import { Form, Input, Button, message, Card } from "antd";
import createAxiosInstance from "../util/axiosInstance"; // Assuming the axios instance is in the util folder

const ForgotPassword = () => {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    try {
      setLoading(true);

      // Create axios instance for auth-related API calls
      const axiosInstance = createAxiosInstance("auth");

      // API call to send the password reset link
      await axiosInstance.post("/auth/forgot-password", {
        email: values.email,
      });

      message.success("Password reset link sent to your email!");
    } catch (error) {
      message.error("Failed to send password reset link. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Card style={{ width: 400 }}>
        <Form name="forgot_password" layout="vertical" onFinish={onFinish}>
          <Form.Item
            name="email"
            label="Email Address"
            rules={[
              { required: true, message: "Please input your email address!" },
              { type: "email", message: "Please enter a valid email!" },
            ]}
          >
            <Input placeholder="Enter your email" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Send Reset Link
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default ForgotPassword;
