/* ============================== IMPORTS ============================== */
import React, { useEffect, useState } from "react";
import {
  Table,
  Button,
  Modal,
  Input,
  Typography,
  Checkbox,
  message,
  Tooltip,
  Form,
  Alert,
} from "antd";
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  GithubOutlined,
  ExclamationCircleOutlined,
  GitlabOutlined,
} from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import {
  useAddRepositoryMutation,
  useUpdateRepositoryMutation,
  useDeleteRepositoryMutation,
} from "../../store/api/cyberService/repositoryAPi";
import ScanTypeTable from "./ScanTypeTable";
import { useCheckFindingsBulkQuery } from "../../store/api/cyberService/scannerApi";

import createAxiosInstance from "../../util/axiosInstance";
import RepositoryProvider from "../../util/auth/OAuthProvider";

/* ============================== CONFIG ============================== */
const { Title } = Typography;
const { confirm } = Modal;

const RepositoriesTab = ({ projectDetails, refetch }) => {
  const [isAddRepoModalVisible, setIsAddRepoModalVisible] = useState(false);
  const [repoDetails, setRepoDetails] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [newRepoName, setNewRepoName] = useState(projectDetails?.repo_url);
  const [isPrivateRepo, setIsPrivateRepo] = useState(false);
  const [accessToken, setAccessToken] = useState("");
  const [editRepoData, setEditRepoData] = useState(null); // Track repo being edited
  const [repositoryLabel, setRepositoryLabel] = useState("");
  const [form] = Form.useForm();
  const [isDeleting, setIsDeleting] = useState(false);

  // Stores the repository provider (GitLab/GitHub) if the repository is private
  // This is only necessary for the private repos because we need to manipualte the link in the cyber-service
  // s.t. the access_token is added correctly
  const [repositoryProvider, setRepositoryProvider] = useState(
    RepositoryProvider.NotApplicable
  );

  const targetIds =
    projectDetails?.repo_url_data?.map((repo) => repo._id) || [];
  const { data, error, isLoading } = useCheckFindingsBulkQuery(targetIds, {
    skip: !targetIds || targetIds.length === 0,
  });

  const [addRepository, { isLoading: isLoadingAddRepo }] =
    useAddRepositoryMutation();
  const [updateRepository] = useUpdateRepositoryMutation();
  const [deleteRepository] = useDeleteRepositoryMutation();

  const selectedProject = useSelector((state) => state.auth.selectedProject);

  useEffect(() => {
    console.log("Render is happening");
    if (projectDetails) {
      setRepoDetails(projectDetails.repo_url_data || []);
    }
  }, [projectDetails]);

  const handleAddRepo = async () => {
    try {
      if (!newRepoName) {
        message.error("Repository name cannot be empty.");
        return;
      }

      if (isPrivateRepo && !accessToken) {
        message.error("Access token is required for private repositories.");
        return;
      }

      // Check that the repository provider is specified
      if (isPrivateRepo && !repositoryProvider) {
        message.error("The repository provider is invalid");
        return;
      }

      await addRepository({
        project_id: projectDetails?._id,
        repository_url: newRepoName,
        access_token: accessToken,
        is_private_repo: isPrivateRepo,
        repository_label: repositoryLabel,
        repository_provider: repositoryProvider,
      }).unwrap();

      setIsAddRepoModalVisible(false);
      setNewRepoName("");
      setIsPrivateRepo(false);
      setAccessToken("");
      setRepositoryProvider(null);
      setRepositoryLabel("");
      message.success("Repository added successfully.");
      refetch(); // Refresh repository list
      setIsEditing(false);
      form.resetFields();
    } catch (error) {
      console.error("Error adding/updating domain:", error);
      message.error(error?.data?.message || "Failed to process request.");
    }
  };

  const handleUpdateRepo = async () => {
    try {
      if (!newRepoName) {
        message.error("Repository name cannot be empty.");
        return;
      }

      const updatedRepoData = {
        repository_url: newRepoName,
        access_token: accessToken,
        is_private_repo: isPrivateRepo,
        target_repository_id: editRepoData._id,
        project_id: projectDetails?._id,
        repository_label: repositoryLabel,
      };

      await updateRepository({
        id: editRepoData._id,
        repositoryData: updatedRepoData,
      }).unwrap();

      message.success("Repository updated successfully.");
      setIsAddRepoModalVisible(false);
      setNewRepoName("");
      setIsPrivateRepo(false);
      setAccessToken("");
      setRepositoryLabel("");
      refetch(); // Refresh repository list
      setEditRepoData(null); // Clear editing state
      form.resetFields();
    } catch (error) {
      console.error("Error adding/updating domain:", error);
      message.error(error?.data?.message || "Failed to process request.");
    }
  };

  const handleEditRepo = (repoData) => {
    setEditRepoData(repoData); // Set the repo data to be edited
    setNewRepoName(repoData.repository_url);
    setIsPrivateRepo(repoData.is_private_repo);
    setAccessToken(repoData.access_token);
    setRepositoryLabel(repoData.repository_label);
    setIsAddRepoModalVisible(true);
    setIsEditing(true); // Set the state to editing mode
  };

  const authenticateWithGitHub = async () => {
    const clientId = import.meta.env.VITE_CLIENT_ID;
    const redirectUri = import.meta.env.VITE_GITHUB_REDIRECT_URI;
    const state = "some_unique_state"; // You can generate a unique state to prevent CSRF attacks
    const githubAppName = import.meta.env.VITE_GITHUB_APP_NAME; // Replace with your actual GitHub app name
    const authUrl = `https://github.com/apps/${githubAppName}/installations/select_target?redirect_uri=${redirectUri}&state=${state}`;

    const authWindow = window.open(authUrl, "_blank", "width=500,height=600");

    const messageListener = (event) => {
      if (event.origin !== window.location.origin) return;

      const { token, error } = event.data;
      if (error) {
        message.error("GitHub authentication failed.");
        return;
      }

      if (token) {
        setAccessToken(token);
        setRepositoryProvider(RepositoryProvider.GitHub);
        message.success("GitHub authentication successful!");
        if (authWindow) {
          authWindow.close();
        }
        window.removeEventListener("message", messageListener);
      }
    };

    window.addEventListener("message", messageListener);
  };

  /**
   * This function handles authentication with GitLab
   * It will first open a popup allowing the user to read the requested permissions
   * Afterwards, if access is granted, the access and refresh tokens will be retrieved and stored as cookies on the backend
   */
  const authenticateWithGitLab = async () => {
    try {
      /* ---------------- CREATE REDIRECTION URL ---------------- */
      // create axios instance
      const axiosInstance = createAxiosInstance("auth");

      // get the state and PKCE pair from the backend
      const response = await axiosInstance.get("/auth/gitlab-parameters");
      const tokens = response.data;
      const state = tokens.state;
      const code_challenge = tokens.code_challenge;

      // Check if both the state and code challenge have been succesfully retrieved from the backend
      if (!state || !code_challenge) {
        throw new Error("Something went wrong. Please try again later");
      }

      const client_id = import.meta.env.VITE_GITLAB_CLIENT_ID;
      const redirect_uri = import.meta.env.VITE_GITLAB_REDIRECT_URI; // redirect URI must become a path to the GitLab OAuth callback
      const response_type = "code";
      const scope = "read_user read_api read_repository";
      const code_challenge_method = "S256";

      // TODO: Create GitLab project as admin and add user who
      // TODO: has min read/write access and try to see if they can authorize the project

      // Build URL
      const gitlabRedirectionURL = `https://gitlab.com/oauth/authorize?client_id=${client_id}&redirect_uri=${redirect_uri}&response_type=${response_type}&state=${state}&scope=${scope}&code_challenge=${code_challenge}&code_challenge_method=${code_challenge_method}`;

      /* ---------------- OPEN NEW WINDOW ---------------- */
      const authWindow = window.open(
        gitlabRedirectionURL,
        "_blank",
        "width=500,height=600"
      );

      //! When modifying this handler, make sure the event listener is removed before a return
      // Listen to incoming messages from the popup window
      // This message should contain the GitLab tokens
      const messageListener = (event) => {
        // Check that the message has been sent from the popup window
        if (event.origin !== window.location.origin) return;

        // Retrieve the message payload
        const { access_token, error } = event.data;

        // Check if an error has occured
        if (error) {
          message.error({
            content: "GitLab authentication failed, please try again later 1",
            key: "gitlab-auth-error",
          });
          window.removeEventListener("message", messageListener);
          return;
        }

        // Check that the access token is present
        if (access_token) {
          setAccessToken(access_token);
          setRepositoryProvider(RepositoryProvider.GitLab);
          message.success("GitLab authentication successful!");
          if (authWindow) {
            authWindow.close();
          }
          window.removeEventListener("message", messageListener);
        }
      };

      window.addEventListener("message", messageListener);
    } catch (error) {
      // TODO: Improve error handling
      message.error(
        "An error occurred during GitLab authentication. Please try again."
      );
    }
  };

  const handleRepositoryDelete = (record) => {
    console.log("Repository Record to Delete:", record);
    const repository_id = record?._id;

    setIsDeleting(true);

    deleteRepository(repository_id)
      .unwrap()
      .then((response) => {
        message.success("Repository configuration deleted successfully!");
        refetch();
      })
      .catch((error) => {
        console.error("Failed to delete Repository configuration:", error);
        message.error(
          "Failed to delete Repository configuration. Please try again."
        );
      })
      .finally(() => {
        setIsDeleting(false);
      });
  };

  const showRepositoryDeleteConfirm = (record) => {
    confirm({
      title: (
        <>
          <ExclamationCircleOutlined
            style={{ color: "red", marginRight: "8px" }}
          />
          Are you sure you want to delete this repository configuration?
        </>
      ),
      content: (
        <div style={{ marginTop: "16px" }}>
          <p>
            Deleting this repository will permanently remove all findings
            related to this resource.
          </p>
        </div>
      ),
      okText: "Yes, delete",
      okType: "danger",
      cancelText: "Cancel",
      centered: true,
      icon: null,
      onOk() {
        handleRepositoryDelete(record);
      },
    });
  };

  const repoColumns = [
    {
      title: "Repository Name",
      dataIndex: "repository_label",
      key: "repository_label",
    },
    {
      title: "Repository URL",
      dataIndex: "repository_url",
      key: "repository_url",
    },
    {
      title: "Private",
      dataIndex: "is_private_repo",
      key: "is_private_repo",
      render: (isPrivate) => (isPrivate ? "Yes" : "No"),
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
              disabled={data?.[record?._id]}
              onClick={() => handleEditRepo(record)}
            />
          </Tooltip>
          <Tooltip title="Remove">
            <Button
              icon={<DeleteOutlined />}
              type="link"
              danger
              onClick={() => showRepositoryDeleteConfirm(record)}
              loading={isDeleting}
            />
          </Tooltip>
        </div>
      ),
    },
  ];

  const handleOpenModal = () => {
    setNewRepoName("");
    setIsPrivateRepo(false);
    setAccessToken("");
    setRepositoryLabel("");
    setIsEditing(false); // Reset editing state
    setEditRepoData(null);
    setIsAddRepoModalVisible(true);
  };

  return (
    <div style={{ padding: "0", borderRadius: "8px" }}>
      <div style={{ textAlign: "right", marginBottom: "16px" }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleOpenModal}
          style={{ background: "#6BE992", boxShadow: "none" }}
          disabled={projectDetails?.repo_url_data?.length >= 1}
        >
          Add Repository
        </Button>
      </div>

      <Table
        dataSource={repoDetails}
        columns={repoColumns}
        rowKey="_id" // Use unique identifier (_id)
        pagination={false}
        style={{ marginTop: "16px" }}
        bordered
      />

      <ScanTypeTable targetTypes={["repo"]} />

      <Modal
        visible={isAddRepoModalVisible}
        onCancel={() => setIsAddRepoModalVisible(false)}
        footer={null} // Custom footer for better control
        bodyStyle={{ padding: "16px" }}
      >
        <Title level={4} style={{ marginBottom: "12px", marginTop: 0 }}>
          {editRepoData ? "Update Repository" : "Add Repository"}
        </Title>
        <Alert
          message="Warning"
          description="Only the repository owner can add a repository to this project."
          type="warning"
          showIcon
          style={{ marginBottom: "16px" }}
        />
        <Form
          form={form}
          layout="vertical"
          onFinish={isEditing ? handleUpdateRepo : handleAddRepo}
          initialValues={{
            repository_url: newRepoName,
            repository_label: repositoryLabel,
            is_private_repo: isPrivateRepo,
          }}
        >
          <Form.Item
            label="Repository URL"
            name="repository_url"
            rules={[{ required: true, message: "Repository URL is required." }]}
            style={{ marginBottom: "12px" }}
          >
            <Input
              value={newRepoName}
              onChange={(e) => setNewRepoName(e.target.value)}
              placeholder="Enter repository URL"
            />
          </Form.Item>

          <Form.Item
            label="Repository Label"
            name="repository_label"
            rules={[
              { required: true, message: "Repository Label is required." },
            ]}
            style={{ marginBottom: "12px" }}
          >
            <Input
              value={repositoryLabel}
              onChange={(e) => setRepositoryLabel(e.target.value)}
              placeholder="Enter repository label"
            />
          </Form.Item>

          <Form.Item
            name="is_private_repo"
            valuePropName="checked"
            style={{ marginBottom: "12px" }}
          >
            <Checkbox
              checked={isPrivateRepo}
              onChange={(e) => {
                // Check if the repository is marked as public again
                if (!e.target.checked) {
                  setRepositoryProvider(RepositoryProvider.NotApplicable);
                }

                // Set the isPrivateRepo flag
                setIsPrivateRepo(e.target.checked);
              }}
            >
              Is this a private repository?
            </Checkbox>
          </Form.Item>

          {isPrivateRepo && (
            <div
              style={{
                display: "flex",
                flexFlow: "row nowrap",
                justifyContent: "space-between",
              }}
            >
              {/* ------------------- GITHUB AUTH ------------------- */}
              <Button
                icon={<GithubOutlined />}
                onClick={authenticateWithGitHub}
                type="primary"
                style={{
                  background: "#6BE992",
                  boxShadow: "none",
                  marginBottom: "12px",
                }}
              >
                Authenticate with GitHub
              </Button>

              {/* ------------------- GITLAB AUTH ------------------- */}
              <Button
                icon={<GitlabOutlined />}
                onClick={authenticateWithGitLab}
                type="primary"
                style={{
                  background: "#6BE992",
                  boxShadow: "none",
                  marginBottom: "12px",
                }}
              >
                Authenticate with GitLab
              </Button>
            </div>
          )}

          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              style={{
                width: "100%",
                padding: "12px",
                marginBottom: 0,
                background: "#6BE992",
                boxShadow: "none",
              }}
              loading={isLoadingAddRepo}
            >
              {editRepoData ? "Update Repository" : "Add Repository"}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default RepositoriesTab;
