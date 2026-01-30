import React, { useEffect, useState } from "react";
import {
  Table,
  Button,
  Modal,
  Input,
  Typography,
  message,
  Tooltip,
  Form,
} from "antd";
import { EditOutlined, DeleteOutlined, PlusOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { useDispatch } from "react-redux";
import { useUpdateProjectMutation } from "../../store/api/cyberService/projectApi";
import { setSelectedProject } from "../../store/authSlice";
import {
  useAddDomainMutation,
  useDeleteDomainMutation,
  useUpdateDomainMutation,
} from "../../store/api/cyberService/domainAPi";
import ScanTypeTable from "./ScanTypeTable";
import { useCheckFindingsBulkQuery } from "../../store/api/cyberService/scannerApi";

const { Text, Title } = Typography;
const { confirm } = Modal;

const DomainTab = ({ projectDetails, refetch }) => {
  const [isAddDomainModalVisible, setIsAddDomainModalVisible] = useState(false);
  const [isDeleteConfirmModalVisible, setIsDeleteConfirmModalVisible] =
    useState(false);
  const [domainDetails, setDomainDetails] = useState([]);
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false); 
  const [form] = Form.useForm();

  const [addDomain, { isLoading: isAdding }] = useAddDomainMutation();
  const [updateDomain] = useUpdateDomainMutation();
  const [deleteDomain] = useDeleteDomainMutation();
  const dispatch = useDispatch();

  const targetIds = projectDetails?.domain_data?.map((repo) => repo._id) || [];
  const { data, error, isLoading } = useCheckFindingsBulkQuery(targetIds, {
    skip: !targetIds || targetIds.length === 0,
  });

  console.log(projectDetails, "project");

  useEffect(() => {
    if (projectDetails) {
      setDomainDetails(
        projectDetails.domain_data ? projectDetails.domain_data : []
      );
    }
  }, [projectDetails]);

  const handleAddOrEditDomain = async (values) => {
    const { domain_url, domain_label } = values;

    try {
      if (selectedDomain) {
        // Editing an existing domain
        const updatedDomainData = {
          domain_url,
          domain_label,
          target_domain_id: selectedDomain._id,
          project_id: projectDetails?._id,
        };

        await updateDomain({
          id: selectedDomain._id,
          domainData: updatedDomainData,
        }).unwrap();

        message.success("Domain updated successfully.");
      } else {
        // Adding a new domain
        await addDomain({
          project_id: projectDetails?._id,
          domain_url,
          domain_label,
        }).unwrap();

        message.success("Domain added successfully.");
      }

      setIsAddDomainModalVisible(false);
      form.resetFields();
      setSelectedDomain(null);
      refetch();
    } catch (error) {
      console.error("Error adding/updating domain:", error);
      message.error(error?.data?.message || "Failed to process request.");
    }
  };

  const handleRemoveDomain = async () => {
    const updatedDomains = domainDetails.filter(
      (domain) => domain._id !== selectedDomain._id
    );

    await updateDomain({
      id: projectDetails?._id,
      projectData: {
        ...projectDetails,
        domain_data: updatedDomains,
      },
    });

    dispatch(
      setSelectedProject({ ...projectDetails, domain_data: updatedDomains })
    );
    setDomainDetails(updatedDomains);
    setIsDeleteConfirmModalVisible(false);
    message.success("Domain deleted successfully.");
  };

  const handleEdit = (record) => {
    setSelectedDomain(record);
    form.setFieldsValue({
      domain_url: record.domain_url,
      domain_label: record.domain_label,
    });
    setIsAddDomainModalVisible(true);
  };

  const handledomainDelete = (record) => {
    console.log("Domain Record to Delete:", record);
    const domain_id = record?._id;

    setIsDeleting(true); 

    deleteDomain(domain_id)
      .unwrap()
      .then((response) => {
        message.success("Domain configuration deleted successfully!");
        refetch();
      })
      .catch((error) => {
        console.error("Failed to delete Domain configuration:", error);
        message.error("Failed to delete Domain configuration. Please try again.");
      })
      .finally(() => {
        setIsDeleting(false); 
      });
  };

  const showDomainDeleteConfirm = (record) => {
    confirm({
      title: (
        <>
          <ExclamationCircleOutlined style={{ color: 'red', marginRight: '8px' }} />
          Are you sure you want to delete this Domain configuration?
        </>
      ),
      content: (
        <div style={{ marginTop: '16px' }}>
          <p>
            Deleting this domain will permanently remove all findings related to this resource.
          </p>
        </div>
      ),
      okText: 'Yes, delete',
      okType: 'danger',
      cancelText: 'Cancel',
      centered: true,
      icon: null,
      onOk() {
        handledomainDelete(record);
      },
    });
  };

  const domainColumns = [
    {
      title: "Domain Name",
      dataIndex: "domain_label",
      key: "domain_label",
      width: "30%",
    },
    {
      title: "Domain URL",
      dataIndex: "domain_url",
      key: "domain_url",
      width: "60%",
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
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Tooltip title="Remove">
            <Button
              icon={<DeleteOutlined />}
              type="link"
              danger
              onClick={() => showDomainDeleteConfirm(record)}
              loading={isDeleting} 
            />
          </Tooltip>
        </div>
      ),
    },
  ];

  return (
    <div style={{ padding: "0px", borderRadius: "8px" }}>
      <div style={{ textAlign: "right", marginBottom: "16px" }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setSelectedDomain(null);
            form.resetFields();
            setIsAddDomainModalVisible(true);
          }}
          loading={isAdding}
          style={{ background: "#6BE992", boxShadow: "none" }}
          disabled={projectDetails?.domain_data?.length === 1}
        >
          Add Domain
        </Button>
      </div>

      <Table
        dataSource={domainDetails}
        columns={domainColumns}
        rowKey="_id"
        pagination={false}
        style={{ marginTop: "16px" }}
        bordered
      />
      <ScanTypeTable targetTypes={["domain"]} pagination={true} />

      {/* Add/Edit Domain Modal */}
      <Modal
        visible={isAddDomainModalVisible}
        onCancel={() => setIsAddDomainModalVisible(false)}
        footer={null}
        bodyStyle={{ padding: "16px" }}
      >
        <Title level={4} style={{ marginBottom: "12px", marginTop: 0 }}>
          {selectedDomain ? "Edit Domain" : "Add Domain"}
        </Title>
        <Form form={form} layout="vertical" onFinish={handleAddOrEditDomain}>
          <Form.Item
            label="Domain URL"
            name="domain_url"
            rules={[{ required: true, message: "Domain URL is required." }]}
            style={{ marginBottom: "15px" }}
          >
            <Input placeholder="Enter domain URL" />
          </Form.Item>

          <Form.Item
            label="Domain Label"
            name="domain_label"
            rules={[{ required: true, message: "Domain Label is required." }]}
            style={{ marginBottom: "25px" }}
          >
            <Input placeholder="Enter domain label" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              style={{
                width: "100%",
                background: "#6BE992",
                boxShadow: "none",
              }}
              loading={isAdding}
            >
              {selectedDomain ? "Update Domain" : "Add Domain"}
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        title="Confirm Delete"
        visible={isDeleteConfirmModalVisible}
        onOk={handleRemoveDomain}
        onCancel={() => setIsDeleteConfirmModalVisible(false)}
        okText="Delete"
        okButtonProps={{ danger: true }}
        cancelText="Cancel"
        bodyStyle={{ padding: "16px" }}
      >
        <Text>Are you sure you want to delete this domain?</Text>
      </Modal>
    </div>
  );
};

export default DomainTab;
