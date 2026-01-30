import React, { useEffect, useState } from "react";
import { Typography, Select } from "antd";
import { useSearchParams } from "react-router-dom"; // Import useSearchParams
import FindingDetailsDrawer from "../components/findings/FindingDetailsDrawer";
import FindingsTable from "../components/findings/FindingsTable";
import { useFetchFindingsByProjectIdQuery } from "../store/api/cyberService/scannerApi";
import { useSelector } from "react-redux";

const { Title } = Typography;
const { Option } = Select;

const Findings = () => {
  const [searchParams, setSearchParams] = useSearchParams(); // Get search params
  const [filteredFindings, setFilteredFindings] = useState([]);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [activeTab, setActiveTab] = useState("1");

  // Get initial values from URL or use defaults
  const initialPage = parseInt(searchParams.get("page")) || 1;
  const initialPageSize = parseInt(searchParams.get("pageSize")) || 10;
  const scanTypeIds = searchParams.get("scanTypeIds");

  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [severityFilter, setSeverityFilter] = useState(
    searchParams.get("severity") || null
  );
  const [statusFilter, setStatusFilter] = useState(
    searchParams.get("status") || null
  );

  const selectedProject = useSelector((state) => state.auth.selectedProject);

  const { data: findingsByProjectData, isLoading: findingsByProjectLoading } =
    useFetchFindingsByProjectIdQuery(
      {
        projectId: selectedProject?._id,
        page: currentPage,
        limit: pageSize,
        severity: severityFilter,
        status: statusFilter,
        scanTypeIds: scanTypeIds?.split(","),
      },
      { skip: !selectedProject?._id }
    );

  // Update findings when data or filters change
  useEffect(() => {
    if (selectedProject && findingsByProjectData?.success) {
      const formattedFindings = formatFindings(findingsByProjectData.data);
      setFilteredFindings(formattedFindings);
    }
  }, [selectedProject, findingsByProjectData, severityFilter, statusFilter]);

  // Update the URL when filters or page change
  useEffect(() => {
    setSearchParams({
      page: currentPage,
      pageSize: pageSize,
      severity: severityFilter || "",
      status: statusFilter || "",
      scanTypeIds: scanTypeIds || "",
    });
  }, [currentPage, pageSize, severityFilter, statusFilter, scanTypeIds]);

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
          : finding?.target_type === "repo"
          ? finding?.target_details?.repository_label
          : finding?.target_type === "cloud"
          ? finding?.target_details?.name
          : finding?.target_type === "web3"
          ? finding?.target_details?.contract_label
          : null,
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
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        Findings
      </Title>

      <div
        style={{ marginBottom: "15px", display: "flex", alignItems: "center" }}
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

export default Findings;
