import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Card, Space, Typography, message } from "antd";
import createAxiosInstance from "../util/axiosInstance";
import { useUpdateProjectMutation } from "../store/api/cyberService/projectApi";
import { useDispatch, useSelector } from "react-redux";
import { setSelectedProject } from "../store/authSlice";

const { Title, Text } = Typography;

const OAuthCallback = () => {
  const location = useLocation();
  const [updateProject, { isLoading }] = useUpdateProjectMutation();
  const selectedProject = useSelector((state) => state.auth.selectedProject);
  const dispatch = useDispatch();

  useEffect(() => {
    const fetchAccessToken = async () => {
      const params = new URLSearchParams(location.search);
      const code = params.get("code");

      if (!code) {
        message.error("Authorization code not found.");
        return;
      }

      try {
        const axiosInstance = createAxiosInstance("auth");
        const response = await axiosInstance.post("/auth/github-oauth", {
          code,
        });

        if (response) {
          const { access_token } = response.data;
          const responseData = await updateProject({
            id: selectedProject?._id,
            projectData: {
              ...selectedProject,
              access_token,
            },
          });
          dispatch(setSelectedProject(responseData?.data?.data));

          // Send the access token to the parent window
          window.opener.postMessage(
            { token: access_token },
            window.location.origin
          );

          // Optionally close the child window automatically
          window.close();
        } else {
          message.error("Failed to retrieve access token.");
        }
      } catch (error) {
        message.error("Error occurred while fetching access token.");
      }
    };

    fetchAccessToken();
  }, [location.search]);

  return (
    <div
      style={{
        padding: "20px",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#f7f7f7",
      }}
    >
      <Card
        style={{
          width: "400px",
          textAlign: "center",
          borderRadius: "8px",
          boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
        }}
      >
        <Space direction="vertical" style={{ width: "100%" }}>
          <Title level={3} style={{ color: "#333" }}>
            Processing Authorization
          </Title>
          <Text type="secondary" style={{ marginBottom: "20px" }}>
            Please wait while we complete the GitHub authentication process.
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default OAuthCallback;
