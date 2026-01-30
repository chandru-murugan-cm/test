import React, { useState, useMemo } from "react";
import {
  ConfigProvider,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Upload,
  DatePicker,
  Popconfirm,
  message,
  Space,
  Tag,
  Tabs,
  Card,
  List,
  Alert,
  Divider,
  Tooltip,
} from "antd";
import {
  UploadOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  ClearOutlined,
  PlusOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import {
  useFetchVaptReportsQuery,
  useUploadVaptReportMutation,
  useUpdateVaptReportMutation,
  useDeleteVaptReportMutation,
  useFetchAllProjectsQuery,
  useFetchAllUsersQuery,
  useFetchUserProjectsQuery,
  useUploadManualVaptJsonMutation,
  useValidateManualVaptJsonMutation,
  useFetchManualVaptFindingsQuery,
  useUpdateManualVaptFindingMutation,
  useDeleteManualVaptFindingMutation,
} from "../store/api/cyberService/vaptReportApi";
import { useSelector } from "react-redux";
import dayjs from "dayjs";

const { Option } = Select;
const { TextArea } = Input;

const MONTH_NAMES = [
  "", "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const SEVERITY_COLORS = {
  critical: "red",
  high: "orange",
  medium: "gold",
  low: "blue",
  informational: "gray",
};

const STATUS_COLORS = {
  open: "red",
  closed: "green",
  ignored: "default",
  "false positive": "purple",
};

const TARGET_TYPE_COLORS = {
  repo: "cyan",
  domain: "blue",
  container: "geekblue",
  cloud: "purple",
  web3: "magenta",
  vm: "volcano",
};

const SEVERITY_OPTIONS = [
  { value: "critical", label: "Critical" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
  { value: "informational", label: "Informational" },
];

const STATUS_OPTIONS = [
  { value: "open", label: "Open" },
  { value: "closed", label: "Closed" },
  { value: "ignored", label: "Ignored" },
  { value: "false positive", label: "False Positive" },
];

const TARGET_TYPE_OPTIONS = [
  { value: "repo", label: "Repository" },
  { value: "domain", label: "Domain" },
  { value: "container", label: "Container" },
  { value: "cloud", label: "Cloud" },
  { value: "web3", label: "Web3" },
  { value: "vm", label: "VM" },
];

const VaptReportManagement = () => {
  // Filter state
  const [filterProject, setFilterProject] = useState(null);
  const [filterUser, setFilterUser] = useState(null);
  const [filterMonth, setFilterMonth] = useState(null);

  // Modal state
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editRecord, setEditRecord] = useState(null);
  const [fileList, setFileList] = useState([]);
  const [editFileList, setEditFileList] = useState([]);

  // Upload modal: selected user for dependent project dropdown
  const [uploadSelectedUser, setUploadSelectedUser] = useState(null);

  // Manual VAPT Upload state
  const [manualVaptForm] = Form.useForm();
  const [manualVaptFileList, setManualVaptFileList] = useState([]);
  const [manualVaptSelectedUser, setManualVaptSelectedUser] = useState(null);
  const [manualVaptPreview, setManualVaptPreview] = useState(null);
  const [manualVaptValidationErrors, setManualVaptValidationErrors] = useState(null);

  // Manual VAPT Findings Management state
  const [findingsFilterProject, setFindingsFilterProject] = useState(null);
  const [findingsFilterUser, setFindingsFilterUser] = useState(null);
  const [findingsFilterSeverity, setFindingsFilterSeverity] = useState(null);
  const [findingsFilterStatus, setFindingsFilterStatus] = useState(null);
  const [findingsFilterTargetType, setFindingsFilterTargetType] = useState(null);
  const [findingsFilterMonth, setFindingsFilterMonth] = useState(null);
  const [isEditFindingModalVisible, setIsEditFindingModalVisible] = useState(false);
  const [editFindingRecord, setEditFindingRecord] = useState(null);
  const [editFindingForm] = Form.useForm();
  const [isViewFindingModalVisible, setIsViewFindingModalVisible] = useState(false);
  const [viewFindingRecord, setViewFindingRecord] = useState(null);

  const [uploadForm] = Form.useForm();
  const [editForm] = Form.useForm();

  // Data queries
  const { data: projectsData, isLoading: isLoadingProjects } = useFetchAllProjectsQuery();
  const { data: usersData, isLoading: isLoadingUsers } = useFetchAllUsersQuery();
  const { data: userProjectsData, isLoading: isLoadingUserProjects } = useFetchUserProjectsQuery(
    uploadSelectedUser,
    { skip: !uploadSelectedUser }
  );
  const { data: manualVaptUserProjectsData, isLoading: isLoadingManualVaptUserProjects } = useFetchUserProjectsQuery(
    manualVaptSelectedUser,
    { skip: !manualVaptSelectedUser }
  );
  // Query for findings filter user's projects
  const { data: findingsFilterUserProjectsData, isLoading: isLoadingFindingsFilterUserProjects } = useFetchUserProjectsQuery(
    findingsFilterUser,
    { skip: !findingsFilterUser }
  );
  // Query for VAPT Reports filter user's projects
  const { data: reportsFilterUserProjectsData, isLoading: isLoadingReportsFilterUserProjects } = useFetchUserProjectsQuery(
    filterUser,
    { skip: !filterUser }
  );

  // Manual VAPT Findings query
  const findingsQueryParams = useMemo(() => {
    const params = {};
    if (findingsFilterProject) params.project_id = findingsFilterProject;
    if (findingsFilterUser) params.user_id = findingsFilterUser;
    if (findingsFilterSeverity) params.severity = findingsFilterSeverity;
    if (findingsFilterStatus) params.status = findingsFilterStatus;
    if (findingsFilterTargetType) params.target_type = findingsFilterTargetType;
    if (findingsFilterMonth) {
      params.year = findingsFilterMonth.year();
      params.month = findingsFilterMonth.month() + 1;
    }
    return params;
  }, [findingsFilterProject, findingsFilterUser, findingsFilterSeverity, findingsFilterStatus, findingsFilterTargetType, findingsFilterMonth]);

  const {
    data: manualFindingsData,
    isLoading: isLoadingManualFindings,
    refetch: refetchManualFindings
  } = useFetchManualVaptFindingsQuery(findingsQueryParams);

  const queryParams = useMemo(() => {
    const params = {};
    if (filterProject) params.project_id = filterProject;
    if (filterUser) params.user_id = filterUser;
    if (filterMonth) {
      params.year = filterMonth.year();
      params.month = filterMonth.month() + 1;
    }
    return params;
  }, [filterProject, filterUser, filterMonth]);

  const { data: reportsData, isLoading: isLoadingReports } = useFetchVaptReportsQuery(queryParams);

  // Mutations
  const [uploadVaptReport, { isLoading: isUploading }] = useUploadVaptReportMutation();
  const [updateVaptReport, { isLoading: isUpdating }] = useUpdateVaptReportMutation();
  const [deleteVaptReport] = useDeleteVaptReportMutation();
  const [uploadManualVaptJson, { isLoading: isUploadingManualVapt }] = useUploadManualVaptJsonMutation();
  const [validateManualVaptJson, { isLoading: isValidatingManualVapt }] = useValidateManualVaptJsonMutation();
  const [updateManualVaptFinding, { isLoading: isUpdatingFinding }] = useUpdateManualVaptFindingMutation();
  const [deleteManualVaptFinding] = useDeleteManualVaptFindingMutation();

  const token = useSelector((state) => state.auth.token);

  // Lookup maps
  const projectMap = useMemo(() => {
    const map = {};
    projectsData?.data?.forEach((p) => { map[p._id] = p.name; });
    return map;
  }, [projectsData]);

  const userMap = useMemo(() => {
    const map = {};
    usersData?.data?.forEach((u) => { map[u._id] = `${u.fname} ${u.lname}`; });
    return map;
  }, [usersData]);

  // Handlers
  const handleClearFilters = () => {
    setFilterProject(null);
    setFilterUser(null);
    setFilterMonth(null);
  };

  // Handler for VAPT Reports user filter change - reset project when user changes
  const handleReportsUserFilterChange = (value) => {
    setFilterUser(value);
    setFilterProject(null); // Reset project when user changes
  };

  const handleUploadOpen = () => {
    uploadForm.resetFields();
    setFileList([]);
    setUploadSelectedUser(null);
    setIsUploadModalVisible(true);
  };

  const handleUploadSubmit = async (values) => {
    if (fileList.length === 0) {
      message.error("Please select a file to upload.");
      return;
    }
    const formData = new FormData();
    formData.append("project_id", values.project_id);
    formData.append("user_id", values.user_id);
    formData.append("year", values.month.year());
    formData.append("month", values.month.month() + 1);
    formData.append("report_name", values.report_name);
    formData.append("report_file", fileList[0].originFileObj);

    try {
      await uploadVaptReport(formData).unwrap();
      message.success("Report uploaded successfully!");
      setIsUploadModalVisible(false);
      uploadForm.resetFields();
      setFileList([]);
      setUploadSelectedUser(null);
    } catch (error) {
      message.error(error?.data?.error || "Failed to upload the report.");
    }
  };

  const handleEditOpen = (record) => {
    setEditRecord(record);
    setEditFileList([]);
    editForm.setFieldsValue({
      report_name: record.report_name,
      month: dayjs().year(record.year).month(record.month - 1),
    });
    setIsEditModalVisible(true);
  };

  const handleEditSubmit = async (values) => {
    const formData = new FormData();
    formData.append("report_name", values.report_name);
    formData.append("year", values.month.year());
    formData.append("month", values.month.month() + 1);
    if (editFileList.length > 0) {
      formData.append("report_file", editFileList[0].originFileObj);
    }

    try {
      await updateVaptReport({
        vapt_report_id: editRecord._id,
        reportData: formData,
      }).unwrap();
      message.success("Report updated successfully!");
      setIsEditModalVisible(false);
      setEditRecord(null);
      setEditFileList([]);
    } catch (error) {
      message.error(error?.data?.error || "Failed to update the report.");
    }
  };

  const handleDelete = async (vapt_report_id) => {
    try {
      await deleteVaptReport(vapt_report_id).unwrap();
      message.success("Report deleted successfully!");
    } catch (error) {
      message.error(error?.data?.error || "Failed to delete the report.");
    }
  };

  const handleDownload = async (record) => {
    try {
      const baseUrl = import.meta.env.VITE_API_CYBER_SERVICE_BASE_URL;
      const response = await fetch(
        `${baseUrl}/crscan/vapt-reports/${record._id}/download`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!response.ok) throw new Error("Download failed");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const contentDisposition = response.headers.get("content-disposition");
      let filename = record.report_name;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=(.+)/);
        if (match) filename = match[1].replace(/"/g, "");
      }
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      message.error("Failed to download the report.");
    }
  };

  // Manual VAPT Upload Handlers
  const handleManualVaptFileChange = async ({ fileList: fl }) => {
    setManualVaptFileList(fl);
    setManualVaptPreview(null);
    setManualVaptValidationErrors(null);

    if (fl.length > 0 && fl[0].originFileObj) {
      const formData = new FormData();
      formData.append("json_file", fl[0].originFileObj);

      try {
        const result = await validateManualVaptJson(formData).unwrap();
        setManualVaptPreview(result);
        setManualVaptValidationErrors(null);
      } catch (error) {
        setManualVaptPreview(null);
        setManualVaptValidationErrors(error?.data?.errors || [error?.data?.error || "Validation failed"]);
      }
    }
  };

  const handleManualVaptSubmit = async (values) => {
    if (manualVaptFileList.length === 0) {
      message.error("Please select a JSON file to upload.");
      return;
    }

    if (manualVaptValidationErrors) {
      message.error("Please fix the validation errors before uploading.");
      return;
    }

    const formData = new FormData();
    formData.append("project_id", values.project_id);
    formData.append("user_id", values.user_id);
    formData.append("json_file", manualVaptFileList[0].originFileObj);

    try {
      const result = await uploadManualVaptJson(formData).unwrap();
      message.success(`Successfully uploaded ${result.data.findings_count} findings!`);
      manualVaptForm.resetFields();
      setManualVaptFileList([]);
      setManualVaptSelectedUser(null);
      setManualVaptPreview(null);
      setManualVaptValidationErrors(null);
      refetchManualFindings();
    } catch (error) {
      message.error(error?.data?.error || "Failed to upload the findings.");
    }
  };

  const handleManualVaptReset = () => {
    manualVaptForm.resetFields();
    setManualVaptFileList([]);
    setManualVaptSelectedUser(null);
    setManualVaptPreview(null);
    setManualVaptValidationErrors(null);
  };

  // Manual VAPT Findings Management Handlers
  const handleClearFindingsFilters = () => {
    setFindingsFilterProject(null);
    setFindingsFilterUser(null);
    setFindingsFilterSeverity(null);
    setFindingsFilterStatus(null);
    setFindingsFilterTargetType(null);
    setFindingsFilterMonth(null);
  };

  // Handler for findings user filter change - reset project when user changes
  const handleFindingsUserFilterChange = (value) => {
    setFindingsFilterUser(value);
    setFindingsFilterProject(null); // Reset project when user changes
  };

  const handleViewFinding = (record) => {
    setViewFindingRecord(record);
    setIsViewFindingModalVisible(true);
  };

  const handleEditFindingOpen = (record) => {
    setEditFindingRecord(record);
    editFindingForm.setFieldsValue({
      finding_name: record.finding_name,
      finding_desc: record.finding_desc,
      severity: record.severity,
      status: record.status,
      target_type: record.target_type,
    });
    setIsEditFindingModalVisible(true);
  };

  const handleEditFindingSubmit = async (values) => {
    try {
      await updateManualVaptFinding({
        finding_id: editFindingRecord.finding_id,
        data: values,
      }).unwrap();
      message.success("Finding updated successfully!");
      setIsEditFindingModalVisible(false);
      setEditFindingRecord(null);
      editFindingForm.resetFields();
    } catch (error) {
      message.error(error?.data?.error || "Failed to update the finding.");
    }
  };

  const handleDeleteFinding = async (finding_id) => {
    try {
      await deleteManualVaptFinding(finding_id).unwrap();
      message.success("Finding deleted successfully!");
    } catch (error) {
      message.error(error?.data?.error || "Failed to delete the finding.");
    }
  };

  const columns = [
    {
      title: "Report Name",
      dataIndex: "report_name",
      width: "20%",
    },
    {
      title: "Project",
      dataIndex: "project_id",
      width: "18%",
      render: (project_id) => projectMap[project_id] || project_id,
    },
    {
      title: "User",
      dataIndex: "user_id",
      width: "15%",
      render: (user_id) => userMap[user_id] || user_id,
    },
    {
      title: "Month / Year",
      width: "12%",
      render: (_, record) => (
        <Tag color="blue">
          {MONTH_NAMES[record.month]} {record.year}
        </Tag>
      ),
    },
    {
      title: "Uploaded At",
      dataIndex: "uploaded_at",
      width: "15%",
      render: (val) => (val ? dayjs(val).format("DD MMM YYYY, HH:mm") : "-"),
    },
    {
      title: "Actions",
      width: "20%",
      render: (_, record) => (
        <Space>
          <Button
            icon={<EditOutlined />}
            onClick={() => handleEditOpen(record)}
            size="small"
          />
          <Button
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record)}
            size="small"
          />
          <Popconfirm
            title="Are you sure you want to delete this report?"
            onConfirm={() => handleDelete(record._id)}
          >
            <Button icon={<DeleteOutlined />} size="small" style={{ color: "red" }} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // Manual VAPT Findings columns
  const findingsColumns = [
    {
      title: "Finding Name",
      dataIndex: "finding_name",
      width: "20%",
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <span style={{ fontWeight: 500 }}>{text}</span>
        </Tooltip>
      ),
    },
    {
      title: "Description",
      dataIndex: "finding_desc",
      width: "25%",
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          {text?.length > 50 ? `${text.substring(0, 50)}...` : text}
        </Tooltip>
      ),
    },
    {
      title: "Severity",
      dataIndex: "severity",
      width: "10%",
      render: (severity) => (
        <Tag color={SEVERITY_COLORS[severity] || "default"}>
          {severity?.toUpperCase()}
        </Tag>
      ),
      filters: SEVERITY_OPTIONS.map(s => ({ text: s.label, value: s.value })),
      onFilter: (value, record) => record.severity === value,
    },
    {
      title: "Status",
      dataIndex: "status",
      width: "10%",
      render: (status) => (
        <Tag color={STATUS_COLORS[status] || "default"}>
          {status?.toUpperCase()}
        </Tag>
      ),
      filters: STATUS_OPTIONS.map(s => ({ text: s.label, value: s.value })),
      onFilter: (value, record) => record.status === value,
    },
    {
      title: "Target Type",
      dataIndex: "target_type",
      width: "10%",
      render: (target_type) => (
        <Tag color={TARGET_TYPE_COLORS[target_type] || "default"}>
          {target_type?.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: "Created",
      dataIndex: "created",
      width: "12%",
      render: (val) => (val ? dayjs(val).format("DD MMM YYYY") : "-"),
      sorter: (a, b) => new Date(a.created) - new Date(b.created),
    },
    {
      title: "Actions",
      width: "13%",
      render: (_, record) => (
        <Space>
          <Tooltip title="View Details">
            <Button
              icon={<EyeOutlined />}
              onClick={() => handleViewFinding(record)}
              size="small"
              type="text"
            />
          </Tooltip>
          <Tooltip title="Edit">
            <Button
              icon={<EditOutlined />}
              onClick={() => handleEditFindingOpen(record)}
              size="small"
              type="text"
              style={{ color: "#1890ff" }}
            />
          </Tooltip>
          <Popconfirm
            title="Delete this finding?"
            description="This action cannot be undone."
            onConfirm={() => handleDeleteFinding(record.finding_id)}
            okText="Delete"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="Delete">
              <Button
                icon={<DeleteOutlined />}
                size="small"
                type="text"
                style={{ color: "red" }}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // Render the VAPT Reports Tab
  const renderVaptReportsTab = () => (
    <>
      <div
        style={{
          display: "flex",
          gap: "12px",
          marginBottom: "16px",
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <Select
          placeholder="Filter by User"
          allowClear
          showSearch
          optionFilterProp="children"
          value={filterUser}
          onChange={handleReportsUserFilterChange}
          loading={isLoadingUsers}
          style={{ width: 220 }}
        >
          {usersData?.data?.map((u) => (
            <Option key={u._id} value={u._id}>
              {u.fname} {u.lname}
            </Option>
          ))}
        </Select>

        <Select
          placeholder={filterUser ? "Filter by Project" : "Select a user first"}
          allowClear
          showSearch
          optionFilterProp="children"
          value={filterProject}
          onChange={setFilterProject}
          loading={isLoadingReportsFilterUserProjects}
          disabled={!filterUser}
          style={{ width: 220 }}
        >
          {reportsFilterUserProjectsData?.data?.map((p) => (
            <Option key={p._id} value={p._id}>
              {p.name}
            </Option>
          ))}
        </Select>

        <DatePicker
          picker="month"
          placeholder="Filter by Month"
          value={filterMonth}
          onChange={setFilterMonth}
          style={{ width: 180 }}
        />

        <Button icon={<ClearOutlined />} onClick={handleClearFilters}>
          Clear
        </Button>

        <div style={{ flex: 1 }} />

        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleUploadOpen}
        >
          Upload Report
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={
          reportsData?.data ? [...reportsData.data].reverse() : []
        }
        rowKey="_id"
        loading={isLoadingReports}
        pagination={{ pageSize: 10 }}
        bordered
      />
    </>
  );

  // Render the Manual VAPT Upload Tab
  const renderManualVaptTab = () => (
    <div>
      {/* Upload Section */}
      <Card title="Upload Manual VAPT Findings" style={{ marginBottom: 24 }}>
        <Alert
          message="JSON File Format"
          description={
            <div>
              <pre style={{ background: "#f5f5f5", padding: 10, borderRadius: 4, fontSize: 12, margin: "8px 0" }}>
{`{
  "findings": [
    {
      "finding_name": "SQL Injection",
      "finding_desc": "Description of the vulnerability",
      "severity": "high",
      "status": "open",
      "target_type": "domain"
    }
  ]
}`}
              </pre>
              <div style={{ fontSize: 12, color: "#666" }}>
                <strong>Valid values:</strong> severity (critical, high, medium, low, informational) |
                status (open, closed, ignored, false positive) |
                target_type (repo, domain, container, cloud, web3, vm)
              </div>
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Form
          layout="vertical"
          form={manualVaptForm}
          onFinish={handleManualVaptSubmit}
        >
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
            <Form.Item
              name="user_id"
              label="User"
              rules={[{ required: true, message: "Please select a user." }]}
              style={{ flex: 1, minWidth: 200 }}
            >
              <Select
                placeholder="Select a user"
                loading={isLoadingUsers}
                showSearch
                optionFilterProp="children"
                onChange={(value) => {
                  setManualVaptSelectedUser(value);
                  manualVaptForm.setFieldsValue({ project_id: undefined });
                }}
              >
                {usersData?.data?.map((u) => (
                  <Option key={u._id} value={u._id}>
                    {u.fname} {u.lname}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="project_id"
              label="Project"
              rules={[{ required: true, message: "Please select a project." }]}
              style={{ flex: 1, minWidth: 200 }}
            >
              <Select
                placeholder={manualVaptSelectedUser ? "Select a project" : "Select a user first"}
                loading={isLoadingManualVaptUserProjects}
                showSearch
                optionFilterProp="children"
                disabled={!manualVaptSelectedUser}
              >
                {manualVaptUserProjectsData?.data?.map((p) => (
                  <Option key={p._id} value={p._id}>
                    {p.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item label="JSON File" required style={{ flex: 1, minWidth: 200 }}>
              <Upload
                fileList={manualVaptFileList}
                onChange={handleManualVaptFileChange}
                beforeUpload={() => false}
                maxCount={1}
                accept=".json"
              >
                <Button icon={<FileTextOutlined />} loading={isValidatingManualVapt}>
                  Select JSON File
                </Button>
              </Upload>
            </Form.Item>
          </div>

          {manualVaptValidationErrors && (
            <Alert
              message="Validation Errors"
              description={
                <List
                  size="small"
                  dataSource={manualVaptValidationErrors}
                  renderItem={(error) => (
                    <List.Item style={{ padding: "4px 0" }}>
                      <CloseCircleOutlined style={{ color: "red", marginRight: 8 }} />
                      {error}
                    </List.Item>
                  )}
                />
              }
              type="error"
              style={{ marginBottom: 16 }}
            />
          )}

          {manualVaptPreview && manualVaptPreview.valid && (
            <Alert
              message={
                <span>
                  <CheckCircleOutlined style={{ color: "green", marginRight: 8 }} />
                  Valid JSON - {manualVaptPreview.findings_count} finding(s) ready to upload
                </span>
              }
              description={
                <List
                  size="small"
                  bordered
                  style={{ marginTop: 8, background: "#fff", maxHeight: 200, overflow: "auto" }}
                  dataSource={manualVaptPreview.preview}
                  renderItem={(finding, index) => (
                    <List.Item style={{ padding: "8px 12px" }}>
                      <div style={{ width: "100%", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span><strong>{index + 1}.</strong> {finding.finding_name}</span>
                        <Space>
                          <Tag color={SEVERITY_COLORS[finding.severity]}>{finding.severity}</Tag>
                          <Tag color={STATUS_COLORS[finding.status]}>{finding.status}</Tag>
                        </Space>
                      </div>
                    </List.Item>
                  )}
                />
              }
              type="success"
              style={{ marginBottom: 16 }}
            />
          )}

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
            <Button onClick={handleManualVaptReset}>Reset</Button>
            <Button
              type="primary"
              htmlType="submit"
              loading={isUploadingManualVapt}
              disabled={!manualVaptPreview?.valid}
            >
              Upload Findings
            </Button>
          </div>
        </Form>
      </Card>

      {/* Findings Management Section */}
      <Card
        title="Manage Manual VAPT Findings"
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refetchManualFindings()}
            loading={isLoadingManualFindings}
          >
            Refresh
          </Button>
        }
      >
        {/* Filters */}
        <div
          style={{
            display: "flex",
            gap: "12px",
            marginBottom: "16px",
            flexWrap: "wrap",
            alignItems: "center",
          }}
        >
          <Select
            placeholder="Filter by User"
            allowClear
            showSearch
            optionFilterProp="children"
            value={findingsFilterUser}
            onChange={handleFindingsUserFilterChange}
            loading={isLoadingUsers}
            style={{ width: 200 }}
          >
            {usersData?.data?.map((u) => (
              <Option key={u._id} value={u._id}>
                {u.fname} {u.lname}
              </Option>
            ))}
          </Select>

          <Select
            placeholder={findingsFilterUser ? "Filter by Project" : "Select a user first"}
            allowClear
            showSearch
            optionFilterProp="children"
            value={findingsFilterProject}
            onChange={setFindingsFilterProject}
            loading={isLoadingFindingsFilterUserProjects}
            disabled={!findingsFilterUser}
            style={{ width: 200 }}
          >
            {findingsFilterUserProjectsData?.data?.map((p) => (
              <Option key={p._id} value={p._id}>
                {p.name}
              </Option>
            ))}
          </Select>

          <Select
            placeholder="Filter by Severity"
            allowClear
            value={findingsFilterSeverity}
            onChange={setFindingsFilterSeverity}
            style={{ width: 150 }}
          >
            {SEVERITY_OPTIONS.map((s) => (
              <Option key={s.value} value={s.value}>
                {s.label}
              </Option>
            ))}
          </Select>

          <Select
            placeholder="Filter by Status"
            allowClear
            value={findingsFilterStatus}
            onChange={setFindingsFilterStatus}
            style={{ width: 150 }}
          >
            {STATUS_OPTIONS.map((s) => (
              <Option key={s.value} value={s.value}>
                {s.label}
              </Option>
            ))}
          </Select>

          <Select
            placeholder="Filter by Target Type"
            allowClear
            value={findingsFilterTargetType}
            onChange={setFindingsFilterTargetType}
            style={{ width: 150 }}
          >
            {TARGET_TYPE_OPTIONS.map((s) => (
              <Option key={s.value} value={s.value}>
                {s.label}
              </Option>
            ))}
          </Select>

          <DatePicker
            picker="month"
            placeholder="Filter by Month"
            value={findingsFilterMonth}
            onChange={setFindingsFilterMonth}
            style={{ width: 150 }}
          />

          <Button icon={<ClearOutlined />} onClick={handleClearFindingsFilters}>
            Clear
          </Button>

          <div style={{ flex: 1 }} />

          <Tag color="blue" style={{ fontSize: 14, padding: "4px 12px" }}>
            Total: {manualFindingsData?.total || 0} findings
          </Tag>
        </div>

        {/* Findings Table */}
        <Table
          columns={findingsColumns}
          dataSource={manualFindingsData?.data || []}
          rowKey="finding_id"
          loading={isLoadingManualFindings}
          pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (total) => `Total ${total} findings` }}
          bordered
          size="middle"
        />
      </Card>
    </div>
  );

  return (
    <ConfigProvider theme={{ token: { colorPrimary: "#6BE992" } }}>
      <div style={{ padding: "15px" }}>
        <div style={{ fontSize: "20px", marginBottom: "10px" }}>
          VAPT Reports
        </div>

        <Tabs
          defaultActiveKey="reports"
          items={[
            {
              key: "reports",
              label: "VAPT Reports",
              children: renderVaptReportsTab(),
            },
            {
              key: "manual-upload",
              label: "Manual VAPT Upload",
              children: renderManualVaptTab(),
            },
          ]}
        />

        {/* Upload Modal */}
        <Modal
          title="Upload VAPT Report"
          open={isUploadModalVisible}
          onCancel={() => { setIsUploadModalVisible(false); setUploadSelectedUser(null); }}
          footer={null}
          destroyOnClose
        >
          <Form
            layout="vertical"
            form={uploadForm}
            onFinish={handleUploadSubmit}
          >
            <Form.Item
              name="user_id"
              label="User"
              rules={[{ required: true, message: "Please select a user." }]}
            >
              <Select
                placeholder="Select a user"
                loading={isLoadingUsers}
                showSearch
                optionFilterProp="children"
                onChange={(value) => {
                  setUploadSelectedUser(value);
                  uploadForm.setFieldsValue({ project_id: undefined });
                }}
              >
                {usersData?.data?.map((u) => (
                  <Option key={u._id} value={u._id}>
                    {u.fname} {u.lname}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="project_id"
              label="Project"
              rules={[{ required: true, message: "Please select a project." }]}
            >
              <Select
                placeholder={uploadSelectedUser ? "Select a project" : "Select a user first"}
                loading={isLoadingUserProjects}
                showSearch
                optionFilterProp="children"
                disabled={!uploadSelectedUser}
              >
                {userProjectsData?.data?.map((p) => (
                  <Option key={p._id} value={p._id}>
                    {p.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="report_name"
              label="Report Name"
              rules={[{ required: true, message: "Please enter a report name." }]}
            >
              <Input placeholder="Enter the report name" />
            </Form.Item>
            <Form.Item
              name="month"
              label="Month"
              rules={[{ required: true, message: "Please select a month." }]}
            >
              <DatePicker picker="month" style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item
              label="Report File"
              rules={[{ required: true, message: "Please select a file." }]}
            >
              <Upload
                fileList={fileList}
                onChange={({ fileList: fl }) => setFileList(fl)}
                beforeUpload={() => false}
                maxCount={1}
              >
                <Button icon={<UploadOutlined />}>Select File</Button>
              </Upload>
            </Form.Item>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
              <Button onClick={() => setIsUploadModalVisible(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit" loading={isUploading}>
                Upload
              </Button>
            </div>
          </Form>
        </Modal>

        {/* Edit Report Modal */}
        <Modal
          title="Edit VAPT Report"
          open={isEditModalVisible}
          onCancel={() => {
            setIsEditModalVisible(false);
            setEditRecord(null);
            setEditFileList([]);
          }}
          footer={null}
          destroyOnClose
        >
          <Form
            layout="vertical"
            form={editForm}
            onFinish={handleEditSubmit}
          >
            <Form.Item label="Project">
              <Input
                disabled
                value={editRecord ? projectMap[editRecord.project_id] || editRecord.project_id : ""}
              />
            </Form.Item>
            <Form.Item label="User">
              <Input
                disabled
                value={editRecord ? userMap[editRecord.user_id] || editRecord.user_id : ""}
              />
            </Form.Item>
            <Form.Item
              name="report_name"
              label="Report Name"
              rules={[{ required: true, message: "Please enter a report name." }]}
            >
              <Input placeholder="Enter the report name" />
            </Form.Item>
            <Form.Item
              name="month"
              label="Month"
              rules={[{ required: true, message: "Please select a month." }]}
            >
              <DatePicker picker="month" style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item label="Replace File (optional)">
              <Upload
                fileList={editFileList}
                onChange={({ fileList: fl }) => setEditFileList(fl)}
                beforeUpload={() => false}
                maxCount={1}
              >
                <Button icon={<UploadOutlined />}>Select New File</Button>
              </Upload>
            </Form.Item>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
              <Button
                onClick={() => {
                  setIsEditModalVisible(false);
                  setEditRecord(null);
                  setEditFileList([]);
                }}
              >
                Cancel
              </Button>
              <Button type="primary" htmlType="submit" loading={isUpdating}>
                Save
              </Button>
            </div>
          </Form>
        </Modal>

        {/* View Finding Modal */}
        <Modal
          title="Finding Details"
          open={isViewFindingModalVisible}
          onCancel={() => {
            setIsViewFindingModalVisible(false);
            setViewFindingRecord(null);
          }}
          footer={[
            <Button key="close" onClick={() => setIsViewFindingModalVisible(false)}>
              Close
            </Button>,
            <Button
              key="edit"
              type="primary"
              icon={<EditOutlined />}
              onClick={() => {
                setIsViewFindingModalVisible(false);
                handleEditFindingOpen(viewFindingRecord);
              }}
            >
              Edit
            </Button>,
          ]}
          width={600}
        >
          {viewFindingRecord && (
            <div>
              <div style={{ marginBottom: 16 }}>
                <strong>Finding Name:</strong>
                <div style={{ fontSize: 16, marginTop: 4 }}>{viewFindingRecord.finding_name}</div>
              </div>
              <Divider />
              <div style={{ marginBottom: 16 }}>
                <strong>Description:</strong>
                <div style={{ marginTop: 4, whiteSpace: "pre-wrap", background: "#f5f5f5", padding: 12, borderRadius: 4 }}>
                  {viewFindingRecord.finding_desc}
                </div>
              </div>
              <Divider />
              <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
                <div>
                  <strong>Severity:</strong>
                  <div style={{ marginTop: 4 }}>
                    <Tag color={SEVERITY_COLORS[viewFindingRecord.severity]} style={{ fontSize: 14 }}>
                      {viewFindingRecord.severity?.toUpperCase()}
                    </Tag>
                  </div>
                </div>
                <div>
                  <strong>Status:</strong>
                  <div style={{ marginTop: 4 }}>
                    <Tag color={STATUS_COLORS[viewFindingRecord.status]} style={{ fontSize: 14 }}>
                      {viewFindingRecord.status?.toUpperCase()}
                    </Tag>
                  </div>
                </div>
                <div>
                  <strong>Target Type:</strong>
                  <div style={{ marginTop: 4 }}>
                    <Tag color={TARGET_TYPE_COLORS[viewFindingRecord.target_type]} style={{ fontSize: 14 }}>
                      {viewFindingRecord.target_type?.toUpperCase()}
                    </Tag>
                  </div>
                </div>
              </div>
              <Divider />
              <div style={{ color: "#888", fontSize: 12 }}>
                <strong>Created:</strong> {viewFindingRecord.created ? dayjs(viewFindingRecord.created).format("DD MMM YYYY, HH:mm") : "-"}
              </div>
            </div>
          )}
        </Modal>

        {/* Edit Finding Modal */}
        <Modal
          title="Edit Finding"
          open={isEditFindingModalVisible}
          onCancel={() => {
            setIsEditFindingModalVisible(false);
            setEditFindingRecord(null);
            editFindingForm.resetFields();
          }}
          footer={null}
          destroyOnClose
          width={600}
        >
          <Form
            layout="vertical"
            form={editFindingForm}
            onFinish={handleEditFindingSubmit}
          >
            <Form.Item
              name="finding_name"
              label="Finding Name"
              rules={[{ required: true, message: "Please enter the finding name." }]}
            >
              <Input placeholder="Enter finding name" />
            </Form.Item>
            <Form.Item
              name="finding_desc"
              label="Description"
              rules={[{ required: true, message: "Please enter the description." }]}
            >
              <TextArea rows={4} placeholder="Enter finding description" />
            </Form.Item>
            <div style={{ display: "flex", gap: 16 }}>
              <Form.Item
                name="severity"
                label="Severity"
                rules={[{ required: true, message: "Please select severity." }]}
                style={{ flex: 1 }}
              >
                <Select placeholder="Select severity">
                  {SEVERITY_OPTIONS.map((s) => (
                    <Option key={s.value} value={s.value}>
                      <Tag color={SEVERITY_COLORS[s.value]}>{s.label}</Tag>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                name="status"
                label="Status"
                rules={[{ required: true, message: "Please select status." }]}
                style={{ flex: 1 }}
              >
                <Select placeholder="Select status">
                  {STATUS_OPTIONS.map((s) => (
                    <Option key={s.value} value={s.value}>
                      <Tag color={STATUS_COLORS[s.value]}>{s.label}</Tag>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                name="target_type"
                label="Target Type"
                rules={[{ required: true, message: "Please select target type." }]}
                style={{ flex: 1 }}
              >
                <Select placeholder="Select target type">
                  {TARGET_TYPE_OPTIONS.map((s) => (
                    <Option key={s.value} value={s.value}>
                      <Tag color={TARGET_TYPE_COLORS[s.value]}>{s.label}</Tag>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px", marginTop: 16 }}>
              <Button
                onClick={() => {
                  setIsEditFindingModalVisible(false);
                  setEditFindingRecord(null);
                  editFindingForm.resetFields();
                }}
              >
                Cancel
              </Button>
              <Button type="primary" htmlType="submit" loading={isUpdatingFinding}>
                Save Changes
              </Button>
            </div>
          </Form>
        </Modal>
      </div>
    </ConfigProvider>
  );
};

export default VaptReportManagement;
