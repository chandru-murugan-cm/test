import React, { useState } from "react";
import { Form, Input, Button, Card, Row, Col, Typography, message } from "antd";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import CryptoJS from "crypto-js";
import { useDispatch } from "react-redux";
import { jwtDecode } from "jwt-decode";
import { login, setSelectedProject } from "../store/authSlice";
import createAxiosInstance from "../util/axiosInstance";
import Logo from "../assets/images/cyber_wacht_logo.svg";

// Custom theme colors
const themePrimaryColor = "#000"; // Your primary color

const { Title, Text } = Typography;

const Login = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const secretKey = "5d0s24DPtqwKHrGN4tHi5o7ze"        //import.meta.env.VITE_CRYPTO_SECRET_KEY;
  if (!secretKey) {
    throw new Error("Secret key is missing.");
  }
  // State to manage loading status
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    console.log("Received values of form: ", values);

    if (!values.username) {
      message.error("Username is required");
      return;
    }
    if (!values.password) {
      message.error("Password is required");
      return;
    }

    // Encrypt the password before sending it to the server
    const encryptedPassword = CryptoJS.AES.encrypt(
      values.password,
      secretKey
    ).toString(); // Use a secure secret key

    try {
      setLoading(true); // Set loading to true when the button is clicked

      const axiosInstance = createAxiosInstance("auth");
      const response = await axiosInstance.post("/auth/login", {
        email: values.username,
        password: encryptedPassword,
        targetUI: "admin",
      });

      // Assuming the API returns a JWT on success
      const jwt = response.data.jwt;

      // Decode the JWT to extract user details
      const decodedToken = jwtDecode(jwt);

      dispatch(login({ token: jwt, user: decodedToken }));
      dispatch(setSelectedProject(null));
      localStorage.setItem("token", jwt);

      // Navigate to home page after successful login
      navigate("/");
      message.success("Login successful!"); // Optional success message
    } catch (error) {
      console.log(error, "error");
      if (error.response) {
        message.error(
          error.response.data.message || "Login failed. Please try again."
        );
      } else {
        message.error("Network error or server is unreachable.");
      }
    } finally {
      setLoading(false); // Set loading to false after the request is done
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
              marginBottom: "4px",
              fontSize: "16px",
              fontWeight: "bold",
            }}
          >
            Admin Login
          </Text>
          <Form
            name="login"
            initialValues={{ remember: true }}
            onFinish={onFinish}
            layout="vertical"
            style={{ padding: "20px" }}
          >
            <Form.Item
              label={<span style={{ color: "#888" }}>Username</span>}
              name="username"
              rules={[
                { required: true, message: "Please input your Username!" },
                {
                  type: "email",
                  message: "The input is not a valid user address!",
                },
              ]}
              style={{ color: "#888" }}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Username"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label={<span style={{ color: "#888" }}>Password</span>}
              name="password"
              rules={[
                { required: true, message: "Please input your Password!" },
              ]}
              style={{ color: "#888" }}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                size="large"
              />
            </Form.Item>

            <Form.Item>
              <a
                href="/forgot-password"
                style={{
                  float: "right",
                  color: themePrimaryColor,
                }}
              >
                Forgot password?
              </a>
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                color="default"
                variant="solid"
                style={{
                  width: "100%",
                  marginBottom: "10px",
                  background: "#6BE992",
                  marginTop: "10px",
                }}
                size="large"
                loading={loading}
              >
                Log In
              </Button>
              {/* <div style={{ textAlign: "center" }}>
                Or{" "}
                <a
                  href="/register"
                  style={{
                    color: themePrimaryColor,
                  }}
                >
                  Register now!
                </a>
              </div> */}
            </Form.Item>
          </Form>
        </Card>
      </Col>
    </Row>
  );
};

export default Login;
