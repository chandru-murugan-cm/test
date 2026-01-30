import React, { useEffect, useState } from "react";
import { Row, Col, Typography, Button, Tooltip as TooltipText } from "antd";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import {
  useFetchDashboardDetailsQuery,
  useFetchFindingsByProjectIdQuery,
} from "../store/api/cyberService/scannerApi";
import { LuCheckSquare } from "react-icons/lu";
import { FaRegSquarePlus } from "react-icons/fa6";
import { IoEyeOffSharp } from "react-icons/io5";
import DashboardCard from "../components/dashboard/DashboardCard";
import SeveritySummaryCard from "../components/dashboard/SeveritySummaryCard";
import { useFetchComplianceSummaryQuery } from "../store/api/cyberService/complianceAp";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import {
  useFetchLanguagesAndFrameworkByProjectIdQuery,
  useFetchLicensesAndSbomQuery,
} from "../store/api/cyberService/repoScanResultsApi.js";
import LanguagePieChart from "../components/dashboard/LanguagePieChart.jsx";
import { BsThreeDots } from "react-icons/bs";
import LicensePieChart from "../components/dashboard/LicensePieChart.jsx";

const { Title } = Typography;

const Dashboard = () => {
  const [filteredFindings, setFilteredFindings] = useState([]);
  const selectedProject = useSelector((state) => state.auth.selectedProject);
  const navigate = useNavigate();

  const { data: findingsByProjectData, isLoading: findingsByProjectLoading } =
    useFetchFindingsByProjectIdQuery(
      { projectId: selectedProject?._id, page: 1, limit: 10 },
      { skip: !selectedProject?._id }
    );

  const { data, error, isLoading } = useFetchDashboardDetailsQuery(
    selectedProject?._id,
    {
      skip: !selectedProject?._id,
    }
  );

  const {
    data: complianceSummary,
    error: complianceSummaryError,
    isLoading: complianceSummaryLoading,
  } = useFetchComplianceSummaryQuery(selectedProject?._id, {
    skip: !selectedProject?._id,
  });

  const { data: licensesAndSbomData } = useFetchLicensesAndSbomQuery(
    selectedProject?._id
  );

  const licenseData = Object.entries(
    licensesAndSbomData?.data?.license_stats || {}
  ).map(([key, value]) => ({
    name: key,
    value,
  }));

  const { data: languagesData } = useFetchLanguagesAndFrameworkByProjectIdQuery(
    selectedProject?._id,
    {
      skip: !selectedProject?._id,
    }
  );

  const languageChartData = {
    labels: languagesData?.data?.map((lang) => lang.language_name) || [],
    datasets: [
      {
        label: "Language Distribution",
        data:
          languagesData?.data?.map((lang) => lang.language_percentage) || [],
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
          "#C9CBCF",
          "#FFCD56",
          "#4D5360",
          "#FF6F61",
        ],
        hoverBackgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
          "#C9CBCF",
          "#FFCD56",
          "#4D5360",
          "#FF6F61",
        ],
      },
    ],
  };

  const findingSummary = data?.data;

  useEffect(() => {
    if (selectedProject && findingsByProjectData?.success) {
      const formattedFindings = formatFindings(findingsByProjectData.data);
      setFilteredFindings(formattedFindings);
    }
  }, [selectedProject, findingsByProjectData]);

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
      scanDate: new Date(finding.created).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
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

  const capitalizeFirstLetter = (string) =>
    string.charAt(0).toUpperCase() + string.slice(1);

  // Format compliance data for the chart
  const complianceChartData = complianceSummary?.data
    ?.filter(
      (item) =>
        item.compliance_type !== "OWASP top 10 breakdown" &&
        item.compliance_type !== ""
    ) // Filter out OWASP
    ?.map((item) => ({
      name: item.compliance_type
        .replace(" compliance overview", "") // Remove " compliance overview"
        .replace("ISO 27001:2022", "ISO 27001:2022") // Keep ISO 27001:2022 as is
        .replace("GDPR Compliance Overview", "GDPR")
        .replace("PCI compliance overview", "PCI")
        .replace("HIPAA compliance overview", "HIPAA")
        .replace("NIS2 compliance overview", "NIS2"),
      Complying: item.complying_count,
      "Not Complying": item.non_complying_count,
      "Manual Evaluation Needed": item.manual_evaluation_needed_count,
    }));

  // Custom colors for bars with gradients
  const barColors = [
    { start: "#6BE992", end: "#4BC0C0" }, // Green gradient
    { start: "#ff4d4f", end: "#ff7f50" }, // Red gradient
    { start: "#ffcc00", end: "#ffa500" }, // Yellow gradient
  ];

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div
          style={{
            backgroundColor: "#fff",
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "10px",
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
          }}
        >
          <p style={{ margin: 0, fontWeight: "bold" }}>{label}</p>
          {payload.map((entry, index) => (
            <p
              key={index}
              style={{
                margin: "5px 0",
                color: entry.color,
              }}
            >
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div
      style={{
        padding: "0 24px",
        minHeight: "100vh",
        margin: "0",
        marginTop: "5px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "2px",
          marginBottom: "20px",
        }}
      >
        <Title level={4} style={{ margin: 0 }}>
          Findings Overview
        </Title>

        <TooltipText title="View Findings">
          <Button
            type="link"
            onClick={() => navigate("/findings")}
            style={{
              padding: 0,
              fontSize: "16px", // Adjust icon size
              marginTop: "8px",
            }}
            icon={<BsThreeDots />}
          />
        </TooltipText>
      </div>

      {/* Cards Section */}
      <Row gutter={[16, 16]} style={{ marginBottom: "30px" }}>
        <SeveritySummaryCard findingSummary={findingSummary} />
        <DashboardCard
          icon={<LuCheckSquare size={50} color="#6BE992" />}
          title="Solved Issues"
          value={findingSummary?.status_counts?.closed}
        />
        <DashboardCard
          icon={<FaRegSquarePlus size={50} color="#6BE992" />}
          title="Open Issues"
          value={findingSummary?.status_counts?.open}
        />
        <DashboardCard
          icon={<IoEyeOffSharp size={50} color="#6BE992" />}
          title="Ignored Issues"
          value={findingSummary?.status_counts?.ignored}
        />
      </Row>

      {/* Compliance Charts Section */}
      <Row gutter={[16, 16]} style={{ marginBottom: "30px" }}>
        <Col span={8}>
          <LicensePieChart data={licenseData} />
        </Col>
        <Col span={8}>
          <div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "2px",
                marginBottom: "20px",
              }}
            >
              <Title level={4} style={{ margin: 0 }}>
                Compliance Overview
              </Title>
            </div>

            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={complianceChartData}
                margin={{ top: 20, right: 30, left: -30, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                <XAxis
                  dataKey="name"
                  tick={{ fill: "#666", fontSize: 12 }}
                  axisLine={{ stroke: "#ddd" }}
                />
                <YAxis
                  tick={{ fill: "#666", fontSize: 12 }}
                  axisLine={{ stroke: "#ddd" }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  wrapperStyle={{
                    paddingTop: "20px",
                  }}
                />
                <Bar
                  dataKey="Complying"
                  fill="url(#complyingGradient)"
                  barSize={30}
                  radius={[5, 5, 0, 0]}
                />
                <Bar
                  dataKey="Not Complying"
                  fill="url(#notComplyingGradient)"
                  barSize={30}
                  radius={[5, 5, 0, 0]}
                />
                <Bar
                  dataKey="Manual Evaluation Needed"
                  fill="url(#manualGradient)"
                  barSize={30}
                  radius={[5, 5, 0, 0]}
                />
                <defs>
                  <linearGradient
                    id="complyingGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor={barColors[0].start} />
                    <stop offset="100%" stopColor={barColors[0].end} />
                  </linearGradient>
                  <linearGradient
                    id="notComplyingGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor={barColors[1].start} />
                    <stop offset="100%" stopColor={barColors[1].end} />
                  </linearGradient>
                  <linearGradient
                    id="manualGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor={barColors[2].start} />
                    <stop offset="100%" stopColor={barColors[2].end} />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Col>
        <Col span={8}>
          <LanguagePieChart data={languageChartData} />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
