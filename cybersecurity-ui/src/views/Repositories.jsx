import React, { useEffect, useState } from "react";
import { Select, Typography, List, Avatar } from "antd"; // Import Avatar for icons
import { useSearchParams } from "react-router-dom";
import { GithubOutlined } from "@ant-design/icons"; // Import an icon
import FindingDetailsDrawer from "../components/findings/FindingDetailsDrawer";
import FindingsTable from "../components/findings/FindingsTable";
import { useFetchFindingsByProjectIdQuery } from "../store/api/cyberService/scannerApi";
import { useSelector } from "react-redux";
import { useFetchRepositoriesQuery } from "../store/api/cyberService/repositoryAPi";

const { Title } = Typography;
const { Option } = Select;

const Repositories = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filteredFindings, setFilteredFindings] = useState([]);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [activeTab, setActiveTab] = useState("1");

  // Get initial values from URL or use defaults
  const initialPage = parseInt(searchParams.get("page")) || 1;
  const initialPageSize = parseInt(searchParams.get("pageSize")) || 10;
  const initialSeverityFilter = searchParams.get("severity") || null;
  const initialStatusFilter = searchParams.get("status") || null;

  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [severityFilter, setSeverityFilter] = useState(initialSeverityFilter);
  const [statusFilter, setStatusFilter] = useState(initialStatusFilter);

  const selectedProject = useSelector((state) => state.auth.selectedProject);

  const { data: findingsByProjectData, isLoading: findingsByProjectLoading } =
    useFetchFindingsByProjectIdQuery(
      {
        projectId: selectedProject?._id,
        page: currentPage,
        limit: pageSize,
        targetType: "repo",
        severity: severityFilter,
        status: statusFilter,
      },
      { skip: !selectedProject?._id }
    );

  const { data: repositories } = useFetchRepositoriesQuery(
    { project_id: selectedProject?._id },
    { skip: !selectedProject?._id }
  );

  const repoDetails = repositories?.data;

  // Update findings when data or filters change
  useEffect(() => {
    if (selectedProject && findingsByProjectData?.success) {
      const formattedFindings = formatFindings(findingsByProjectData.data);
      setFilteredFindings(formattedFindings);
    }
  }, [selectedProject, findingsByProjectData]);

  // Update the URL when filters or page change
  useEffect(() => {
    setSearchParams({
      page: currentPage,
      pageSize: pageSize,
      severity: severityFilter || "",
      status: statusFilter || "",
    });
  }, [currentPage, pageSize, severityFilter, statusFilter]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [statusFilter, severityFilter]);

  const formatFindings = (data) => {
    return data.map((finding, index) => ({
      ...finding,
      key: index.toString(),
      findings: finding?.finding_name || "N/A",
      target: finding.target || "N/A",
      riskLevel: finding.severity
        ? capitalizeFirstLetter(finding.severity)
        : "Medium",
      sourceScanners: finding.scanner_categories?.join(", ") || "Unknown",
      scanDate: new Date(finding.created).toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true,
      }),
      scheduledDate: new Date(finding.created).toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }),
      targetType:
        finding?.target_type === "domain"
          ? finding?.target_details?.domain_label
          : finding?.target_details?.repository_label,
      scanType: finding?.scan_type_details?.scan_type || "Other",
    }));
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const capitalizeFirstLetter = (string) =>
    string.charAt(0).toUpperCase() + string.slice(1);

  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={4} style={{ marginBottom: "8px", marginTop: 0 }}>
        Repositories
      </Title>

      {/* Display Repository List with Icons */}
      <List
        dataSource={repoDetails}
        renderItem={(repo) => (
          <List.Item
            style={{
              padding: "12px 0",
            }}
          >
            <List.Item.Meta
              avatar={<GithubOutlined />}
              title={
                <a
                  href={repo.repository_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "#000", fontWeight: 500 }}
                >
                  {repo.repository_label}
                </a>
              }
            />
          </List.Item>
        )}
        style={{ marginBottom: "12px", borderBottom: "1px solid #f0f0f0" }}
      />

      <div
        style={{
          marginBottom: "15px",
          display: "flex",
          alignItems: "center",
          marginTop: "20px",
        }}
      >
        <label style={{ marginRight: "6px", color: "#888" }}>Filter By</label>
        <div style={{ marginRight: "15px", width: "150px" }}>
          <Select
            placeholder="Select Severity"
            style={{ width: "100%" }}
            value={severityFilter}
            onChange={(value) => setSeverityFilter(value)}
            allowClear
          >
            <Option value="high">High</Option>
            <Option value="medium">Medium</Option>
            <Option value="low">Low</Option>
            <Option value="critical">Critical</Option>
            <Option value="informational">Informational</Option>
          </Select>
        </div>
        <div style={{ width: "150px" }}>
          <Select
            placeholder="Select Status"
            style={{ width: "100%" }}
            value={statusFilter}
            onChange={(value) => setStatusFilter(value)}
            allowClear
          >
            <Option value="open">Open</Option>
            <Option value="closed">Closed</Option>
            <Option value="false positive">False Positive</Option>
            <Option value="ignored">Ignored</Option>
          </Select>
        </div>
      </div>

      <FindingsTable
        filteredFindings={filteredFindings}
        loading={findingsByProjectLoading}
        onRowClick={setSelectedFinding}
        setDrawerVisible={setDrawerVisible}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        totalPages={findingsByProjectData?.pagination?.total_pages || 1}
        setPageSize={setPageSize}
      />

      <FindingDetailsDrawer
        onClose={() => {
          setActiveTab("1");
          setDrawerVisible(false);
        }}
        visible={drawerVisible}
        selectedFinding={selectedFinding}
        setSelectedFinding={setSelectedFinding}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />
    </div>
  );
};

export default Repositories;
