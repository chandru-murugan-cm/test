import React, { useState } from "react";
import { Card, Typography, Modal, Input, message } from "antd";
import { EditOutlined } from "@ant-design/icons";
import { useUpdateProjectMutation } from "../../store/api/cyberService/projectApi";
import { useDispatch } from "react-redux";
import { setSelectedProject } from "../../store/authSlice";

const { Text } = Typography;

const ProjectInfoCard = ({ projectDetails }) => {
  const [updateProject, { isLoading }] = useUpdateProjectMutation();
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const dispatch = useDispatch();
  const [newProjectName, setNewProjectName] = useState(projectDetails?.name);
  const [newProjectDescription, setNewProjectDescription] = useState(
    projectDetails?.description || ""
  );

  const handleEditModalOk = async () => {
    try {
      const response = await updateProject({
        id: projectDetails?._id,
        projectData: {
          ...projectDetails,
          name: newProjectName,
          description: newProjectDescription,
        },
      });
      dispatch(setSelectedProject(response?.data?.data));
      message.success("Project updated successfully.");
      setIsEditModalVisible(false);
    } catch (error) {
      message.error("Failed to update the project. Please try again.");
    }
  };

  return (
    <>
      <Card title="Project Details" bordered={false} style={cardStyle}>
        <div>
          <Text strong>Name</Text>
          <br />
          <span style={{ color: "#888888" }}>{projectDetails?.name}</span>
        </div>
        <div style={{ marginTop: "8px" }}>
          <Text strong>Description</Text>
          <br />
          <span style={{ color: "#888888" }}>
            {projectDetails?.description}
          </span>
        </div>
      </Card>

      <Modal
        title="Edit Project"
        visible={isEditModalVisible}
        onOk={handleEditModalOk}
        onCancel={() => setIsEditModalVisible(false)}
        confirmLoading={isLoading}
        okText="Save"
      >
        <Input
          value={newProjectName}
          onChange={(e) => setNewProjectName(e.target.value)}
          placeholder="Enter new Project name"
          style={{ marginBottom: "12px" }}
        />
        <Input.TextArea
          value={newProjectDescription}
          onChange={(e) => setNewProjectDescription(e.target.value)}
          placeholder="Enter new Project description"
          rows={4}
        />
      </Modal>
    </>
  );
};

const cardStyle = {
  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
  borderRadius: "8px",
  padding: "8px",
  marginBottom: "20px",
  width: "100%",
  position: "relative",
};

const editIconStyle = {
  position: "absolute",
  top: "16px",
  right: "16px",
  fontSize: "18px",
  color: "#113032",
};

export default ProjectInfoCard;
