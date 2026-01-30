/* ========================= IMPORTS ========================= */
// core
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

// antd
import { Card, Space, Typography, message } from "antd";
const { Title, Text } = Typography;

// API
import createAxiosInstance from "../util/axiosInstance";

// Redux
import { useDispatch, useSelector } from "react-redux";
import { useUpdateProjectMutation } from "../store/api/cyberService/projectApi";
import { setSelectedProject } from "../store/authSlice";
/* ========================= CONFIG ========================= */
let initializationComplete = false; // variable needed to stop useEffect from running twice while in Strict Mode

const GitLabOAuthCallback = () => {
  const location = useLocation();
  const selectedProject = useSelector((state) => state.auth.selectedProject);
  const [updateProject, { isLoading }] = useUpdateProjectMutation();
  const dispatch = useDispatch();

  useEffect(() => {
    if (!initializationComplete) {
      const fetchAccessToken = async () => {
        /* ---------------- RETRIEVE URL PARAMETERS ----------------*/
        // Get the authorization code
        const urlParams = new URLSearchParams(location.search);
        const code = urlParams.get("code");
        const state = urlParams.get("state");

        // TODO: Retrieve state from the backend and make sure it matches the one from the URL

        // Check that the code search parameter exists
        if (!code) {
          message.error("Authorization code not found.");
          return;
        }

        /* ---------------- FETCH TOKENS ---------------- */
        try {
          // Create the Axios instance
          const axiosInstance = createAxiosInstance("auth");
          const tokenRetrievalResponse = await axiosInstance.post(
            "/auth/gitlab-oauth",
            {
              code,
              state,
            }
          );

          /* ---------------- UPDATE PROJECT ---------------- */
          const { access_token, refresh_token, created_at, expires_in } =
            tokenRetrievalResponse.data;

          const projectUpdateResponse = await updateProject({
            id: selectedProject?._id,
            projectData: {
              ...selectedProject,
              access_token,
            },
          });

          dispatch(setSelectedProject(projectUpdateResponse?.data?.data));

          // Send the access back to the parent window
          window.opener.postMessage(
            { access_token, refresh_token, created_at, expires_in },
            window.location.origin
          );

          // Close the child window
          window.close();
        } catch (error) {
          window.opener.postMessage(
            { error: `${error.message} - ${error.response.data.error}` },
            window.location.origin
          );
          window.close();
        }
      };

      fetchAccessToken();
      initializationComplete = true;
    }
  });

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
            Please wait while we complete the GitLab authentication process.
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default GitLabOAuthCallback;
