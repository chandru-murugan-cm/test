import React from "react";
import { Typography, Row, Col, Card, Tabs, Statistic } from "antd";
import LicenceOverview from "../components/licenceSbom/LicenceOverview";
import { useSelector } from "react-redux";
import LicenceGroups from "../components/licenceSbom/LicenceGroups";
import { useFetchLicensesAndSbomQuery } from "../store/api/cyberService/repoScanResultsApi.js";
import { Pie } from "@ant-design/charts";
import SbomVul from "../components/licenceSbom/SbomVuln.jsx";
import Licenses from "../components/licenceSbom/Licenses.jsx";

const { Title } = Typography;
const { TabPane } = Tabs;

// Define colors for the pie/doughnut charts
const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#AF19FF"];

function LicenceSbom() {
  const selectedProject = useSelector((state) => state.auth.selectedProject);
  const { data: licensesAndSbomData, error, isLoading } = useFetchLicensesAndSbomQuery(selectedProject?._id);
  console.log("licensesAndSbomData", licensesAndSbomData);

  // Data Mapping for Charts
  const severityData = Object.entries(licensesAndSbomData?.data?.severity_stats || {}).map(([key, value]) => ({
    name: key,
    value,
  }));

  const licenseData = Object.entries(licensesAndSbomData?.data?.license_stats || {}).map(([key, value]) => ({
    name: key,
    value,
  }));
  // Pie Chart for License Stats
  const renderLicensePieChart = () => (
    <Card title="License Stats" bordered={false}>
      <Pie
        data={licenseData}
        angleField="value"
        colorField="name"
        radius={0.8}
        label={{ type: "outer", content: "{name} {percentage}" }}
        legend={{ position: "bottom" }}
        color={COLORS}
      />
    </Card>
  );

  // Doughnut Chart for Severity Stats
  const renderSeverityDoughnutChart = () => (
    <Card title="Severity Stats" bordered={false}>
      <Pie
        data={severityData}
        angleField="value"
        colorField="name"
        radius={0.8}
        innerRadius={0.4}
        label={{ type: "outer", content: "{name} {percentage}" }}
        legend={{ position: "bottom" }}
        color={COLORS}
      />
    </Card>
  );

  const renderSummaryCards = () => (
    <Row gutter={16} justify="center" style={{ marginBottom: "24px" }}>
      <Col xs={24} sm={12} md={6}>
        <Card
          style={{
            backgroundColor: "#fafafa",
            borderRadius: "10px",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
            textAlign: "center",
          }}
        >
          <Statistic
            title="Total Packages"
            value={licensesAndSbomData?.data?.summary_stats?.total_packages}
            valueStyle={{ fontSize: "28px", fontWeight: "bold", color: "#1890ff" }}
          />
        </Card>
      </Col>
      <Col xs={24} sm={12} md={6}>
        <Card
          style={{
            backgroundColor: "#fafafa",
            borderRadius: "10px",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
            textAlign: "center",
          }}
        >
          <Statistic
            title="Unique Packages"
            value={licensesAndSbomData?.data?.summary_stats?.unique_package_count}
            valueStyle={{ fontSize: "28px", fontWeight: "bold", color: "#52c41a" }}
          />
        </Card>
      </Col>
    </Row>
  );

  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={4} style={{ marginBottom: "15px", marginTop: 0 }}>
        Licence & SBOM
      </Title>

      {/* Summary cards */}
      {renderSummaryCards()}

      {/* Layout for charts */}
      {/* <Row gutter={[16, 16]} justify="center">
        <Col xs={24} sm={12} md={10}>
          {renderLicensePieChart()}
        </Col>
        <Col xs={24} sm={12} md={10}>
          {renderSeverityDoughnutChart()}
        </Col>
      </Row> */}

      <Tabs defaultActiveKey="1" type="line" style={{ marginTop: "24px" }}>
        <TabPane tab="Packages" key="1">
          <LicenceOverview project_id={selectedProject?._id} />
        </TabPane>
        <TabPane tab="Licenses" key="2">
          <Licenses project_id={selectedProject?._id} />
        </TabPane>
        <TabPane tab="Licence Groups" key="3">
          <LicenceGroups project_id={selectedProject?._id} />
        </TabPane>
        <TabPane tab="Vulnerabilites" key="4">
          <SbomVul project_id={selectedProject?._id} />
        </TabPane>
      </Tabs>
    </div>
  );
}

export default LicenceSbom;
