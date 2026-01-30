import React, { useState } from "react";
import { Form, Input, Button, message, Card } from "antd";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import createAxiosInstance from "../util/axiosInstance";

const ResetPassword = () => {
  const { token } = useParams(); // Get the token from the URL
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    try {
      setLoading(true);
      // Call backend API to reset the password using the token
      const axiosInstance = createAxiosInstance("auth");
      const response = await axiosInstance.post("/auth/reset-password", {
        password: values.password,
        token, // Include the token from the URL
      });
      console.log("response", response)
      message.success("Password successfully reset!");
      navigate("/login"); // Redirect to login after successful reset
    } catch (error) {
      message.error("Failed to reset password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
      <Card style={{ width: 400 }}>
        <Form name="reset_password" layout="vertical" onFinish={onFinish}>
          <Form.Item
            name="password"
            label="New Password"
            rules={[
              { required: true, message: "Please input your new password!" },
            ]}
          >
            <Input.Password placeholder="Enter your new password" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Reset Password
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default ResetPassword;
