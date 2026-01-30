import React from "react";
import { Form, Input, Button, Card, Row, Col, Typography, message } from "antd";
import { LockOutlined, UserOutlined, MailOutlined } from "@ant-design/icons";
import CryptoJS from "crypto-js";
import { useNavigate } from "react-router-dom";
import createAxiosInstance from "../util/axiosInstance";
import Logo from "../assets/images/cyber_wacht_logo.svg";

// Custom theme colors
const themePrimaryColor = "#000"; // Your primary color

const { Title, Text } = Typography;

const Register = () => {
  const navigate = useNavigate();
  const secretKey = import.meta.env.VITE_CRYPTO_SECRET_KEY;

  const onFinish = async (values) => {
    try {
      // Encrypt the password and confirmPassword before sending
      const encryptedPassword = CryptoJS.AES.encrypt(
        values.password,
        secretKey
      ).toString();
      const encryptedConfirmPassword = CryptoJS.AES.encrypt(
        values.confirm,
        secretKey
      ).toString();

      // Prepare the payload for the API
      const payload = {
        fname: values.firstName, // First Name
        lname: values.lastName, // Last Name
        email: values.email,
        organization: values.organization, // Organization Name
        password: encryptedPassword,
        confirmPassword: encryptedConfirmPassword,
      };

      // Make API request to the /auth/register endpoint
      const axiosInstance = createAxiosInstance("auth");
      await axiosInstance.post("/auth/register", payload);

      message.success("Registration successful!");
      navigate("/login");
    } catch (error) {
      if (error.response) {
        if (error.response.data && error.response.data.response) {
          message.error(error.response.data.response.text);
        } else {
          message.error("An error occurred during registration.");
        }
      } else {
        message.error("Network error or server is unreachable.");
      }
    }
  };

  return (
    <Row
      justify="center"
      align="middle"
      style={{
        minHeight: `100vh`,
        backgroundColor: "#f0f2f5",
      }}
    >
      <Col xs={22} sm={18} md={12} lg={8}>
        <Card
          bordered={false}
          style={{
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
            textAlign: "center",
          }}
          bodyStyle={{ padding: "0 24px" }}
        >
          <div style={{ margin: "24px", marginBottom: "12px" }}>
            <img
              src={Logo}
              alt="DCC CyberWacht Logo"
              style={{
                maxWidth: "250px",
                width: "100%",
                height: "auto",
                display: "block",
                margin: "0 auto",
              }}
            />
          </div>
          <Text
            style={{
              display: "block",
              textAlign: "center",
              color: "#555",
              marginBottom: "14px",
              fontSize: "16px",
              fontWeight: "bold",
            }}
          >
            Create Your Account
          </Text>
          <Form
            name="register"
            initialValues={{ remember: true }}
            onFinish={onFinish}
            layout="vertical"
            style={{ padding: "20px" }}
          >
            <Form.Item
              label={<span style={{ color: "#888" }}>First Name</span>}
              name="firstName"
              style={{ marginBottom: "12px" }}
              rules={[
                { required: true, message: "Please input your First Name!" },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="First Name"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label={<span style={{ color: "#888" }}>Last Name</span>}
              name="lastName"
              style={{ marginBottom: "12px" }}
              rules={[
                { required: true, message: "Please input your Last Name!" },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Last Name"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label={<span style={{ color: "#888" }}>Email</span>}
              Last
              Name
              name="email"
              style={{ marginBottom: "12px" }}
              rules={[
                {
                  required: true,
                  message: "Please input your Email!",
                  type: "email",
                },
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="Email"
                size="large"
              />
            </Form.Item>

            {/* Organization Name */}
            <Form.Item
              label={<span style={{ color: "#888" }}>Organization Name</span>}
              name="organization"
              style={{ marginBottom: "12px" }}
              rules={[
                {
                  required: true,
                  message: "Please input your Organization Name!",
                },
              ]}
            >
              <Input placeholder="Organization Name" size="large" />
            </Form.Item>

            <Form.Item
              label={<span style={{ color: "#888" }}>Password</span>}
              name="password"
              style={{ marginBottom: "12px" }}
              rules={[
                { required: true, message: "Please input your Password!" },
                { min: 6, message: "Password must be at least 6 characters." },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label={<span style={{ color: "#888" }}>Confirm Password</span>}
              name="confirm"
              style={{ marginBottom: "18px" }}
              dependencies={["password"]}
              rules={[
                { required: true, message: "Please confirm your Password!" },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue("password") === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(
                      new Error(
                        "The two passwords that you entered do not match!"
                      )
                    );
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Confirm Password"
                size="large"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: "0px" }}>
              <Button
                type="primary"
                htmlType="submit"
                color="default"
                variant="solid"
                style={{
                  width: "100%",
                  marginBottom: "10px",
                  background: "#6BE992",
                }}
                size="large"
              >
                Register
              </Button>
              <div style={{ textAlign: "center" }}>
                Already have an account?{" "}
                <a
                  href="/login"
                  style={{
                    color: themePrimaryColor,
                  }}
                >
                  Log In
                </a>
              </div>
            </Form.Item>
          </Form>
        </Card>
      </Col>
    </Row>
  );
};

export default Register;
