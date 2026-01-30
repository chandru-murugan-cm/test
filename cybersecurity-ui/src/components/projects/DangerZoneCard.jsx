import React, { useState } from "react";
import { Card, Typography, Modal, Button, message } from "antd";
import { DeleteOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { useDeleteProjectMutation } from "../../store/api/cyberService/projectApi";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { setSelectedProject } from "../../store/authSlice";

const { Text } = Typography;

const DangerZoneCard = ({ projectDetails }) => {
  const [isDeleteModalVisible, setIsDeleteModalVisible] = useState(false);
  const [deleteProject] = useDeleteProjectMutation();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleDeleteProject = async () => {
    await deleteProject(projectDetails?._id).unwrap();
    dispatch(setSelectedProject({}));
    message.success("Project deleted successfully.");
    setIsDeleteModalVisible(false);
    navigate("/");
  };

  return (
    <>
      <Card
        bordered={false}
        style={{ border: "1px solid red" }}
        title={
          <div style={{ color: "red", display: "flex", alignItems: "center" }}>
            <ExclamationCircleOutlined style={{ marginRight: "8px" }} />
            Danger Zone
          </div>
        }
      >
        <Text type="danger">
          Deleting this Project will remove all access and associated data for
          all users. This action cannot be undone.
        </Text>
        <div style={{ marginTop: "16px" }}>
          <Button
            type="primary"
            danger
            icon={<DeleteOutlined />}
            onClick={() => setIsDeleteModalVisible(true)}
          >
            Delete Project
          </Button>
        </div>
      </Card>

      <Modal
        title="Confirm Deletion"
        visible={isDeleteModalVisible}
        onOk={handleDeleteProject}
        onCancel={() => setIsDeleteModalVisible(false)}
        okText="Delete"
        okButtonProps={{ danger: true }}
      >
        <Text type="danger">
          Are you sure you want to delete this Project? This action cannot be
          undone.
        </Text>
      </Modal>
    </>
  );
};

export default DangerZoneCard;
