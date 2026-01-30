import React, { useEffect, useState } from "react";
import { Select, Typography } from "antd";
import FindingDetailsDrawer from "../components/findings/FindingDetailsDrawer";
import FindingsTable from "../components/findings/FindingsTable";
import { useFetchFindingsByProjectIdQuery } from "../store/api/cyberService/scannerApi";
import { useSelector } from "react-redux";

const { Title } = Typography;

const Contract = () => {
  const [filteredFindings, setFilteredFindings] = useState([]);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [activeTab, setActiveTab] = useState("1");
  const [severityFilter, setSeverityFilter] = useState(null);
  const [statusFilter, setStatusFilter] = useState(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const selectedProject = useSelector((state) => state.auth.selectedProject);

  const { data: findingsByProjectData, isLoading: findingsByProjectLoading } =
    useFetchFindingsByProjectIdQuery(
      {
        projectId: selectedProject?._id,
        page: currentPage,
        limit: pageSize,
        targetType: "web3",
        severity: severityFilter,
        status: statusFilter,
      },
      { skip: !selectedProject?._id }
    );

  useEffect(() => {
    if (selectedProject && findingsByProjectData?.success) {
      const formattedFindings = formatFindings(findingsByProjectData.data);
      setFilteredFindings(formattedFindings);
    }
  }, [selectedProject, findingsByProjectData]);

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
        finding?.target_type === "web3"
          ? finding?.target_details?.contract_label
          : finding?.target_details?.contract_label,
      scanType: finding?.scan_type_details?.scan_type || "Other",
    }));
  };

  const handlePageChange = (page) => {
    console.log(page, "page");
    setCurrentPage(page);
  };

  const capitalizeFirstLetter = (string) =>
    string.charAt(0).toUpperCase() + string.slice(1);

  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        Web3
      </Title>

      <div
        style={{ marginBottom: "15px", display: "flex", alignItems: "center" }}
      >
        <label style={{ marginRight: "6px", color: "#888" }}>Filter By</label>
        <div style={{ marginRight: "15px", width: "150px" }}>
          <Select
            placeholder="Select Severity"
            style={{ width: "100%" }}
            onChange={setSeverityFilter}
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
            onChange={setStatusFilter}
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

export default Contract;
