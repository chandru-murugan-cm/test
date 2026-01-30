import React, { useState } from "react";
import { Table, Tag, Typography, Space, Drawer, Button, List, Tabs, Descriptions, Badge, Card, Row, Col, Divider, Collapse } from "antd";
import { useFetchSbomVulnQuery } from "../../store/api/cyberService/repoScanResultsApi.js";
import { ArrowRightOutlined, CaretRightOutlined, CheckCircleOutlined, CodeOutlined, LinkOutlined } from "@ant-design/icons";

const { Text, Title } = Typography;
const { Panel } = Collapse;
function SbomVul({ project_id }) {
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [drawerData, setDrawerData] = useState(null);

  const { data: sbom_vul_data, isLoading, error } = useFetchSbomVulnQuery(project_id);
  console.log("sbom_vul_data", sbom_vul_data);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error fetching licenses data!</div>;

  const riskFilters = [
    { text: "High", value: "HIGH" },
    { text: "Medium", value: "MEDIUM" },
    { text: "Low", value: "LOW" },
    { text: "Unknown", value: "UNKNOWN" },
  ];

  const getRiskTagColor = (risk_level) => {
    switch (risk_level) {
      case "HIGH":
        return "volcano";
      case "MEDIUM":
        return "gold";
      case "LOW":
        return "green";
      case "UNKNOWN":
        return "grey";
      default:
        return "blue";
    }
  };

  const columns = [
    {
      title: "Package Name",
      dataIndex: "pkg_name",
      key: "pkg_name",
      filters: [...new Set(sbom_vul_data?.data?.map((group) => group.pkg_name))]?.map((pkgName) => ({
        text: pkgName,
        value: pkgName,
      })),
      onFilter: (value, record) => record.pkg_name === value,
      render: (pkg_name) => <Tag color="blue">{pkg_name}</Tag>,
    },
    {
      title: "Vulnerability ID",
      dataIndex: "vulnerabilityid",
      key: "vulnerabilityid",
      filters: [...new Set(sbom_vul_data?.data?.map((group) => group.vulnerabilityid))]?.map((vulnerabilityid) => ({
        text: vulnerabilityid,
        value: vulnerabilityid,
      })),
      onFilter: (value, record) => record.vulnerabilityid === value,
      render: (vulnerabilityid) => <Tag color="blue">{vulnerabilityid}</Tag>,
    },
    {
      title: "Installed Version",
      dataIndex: "installed_version",
      key: "installed_version",
      render: (installed_version) => installed_version || "N/A",
    },
    {
      title: "Fixed Version",
      dataIndex: "fixed_version",
      key: "fixed_version",
      render: (fixed_version) => fixed_version || "N/A",
    },
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      filters: [...new Set(sbom_vul_data?.data?.map((group) => group.severity))]?.map((severity) => ({
        text: severity,
        value: severity,
      })),
      onFilter: (value, record) => record.severity === value,
      render: (severity) => {
        const color = severity === "HIGH" ? "red" : severity === "MEDIUM" ? "orange" : "green";
        return <Tag color={color}>{severity}</Tag>;
      },
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      filters: [...new Set(sbom_vul_data?.data?.map((group) => group.status))]?.map((status) => ({
        text: status,
        value: status,
      })),
      onFilter: (value, record) => record.status === value,
      render: (status) => {
        const color = status === "fixed" ? "green" : "red";
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: "Advisory",
      dataIndex: "primary_url",
      key: "primary_url",
      render: (url) => (
        <a href={url} target="_blank" rel="noopener noreferrer">
          {url ? "View Advisory" : "N/A"}
        </a>
      ),
    },
    {
      title: "Action",
      key: "action",
      render: (record) => (
        <Button type="primary" onClick={() => openDrawer(record)}>
          View Details
        </Button>
      ),
    },
  ];

  const openDrawer = (record) => {
    setDrawerData(record);
    setDrawerVisible(true);
  };

  const closeDrawer = () => {
    setDrawerVisible(false);
    setDrawerData(null);
  };

  const dataSource = sbom_vul_data?.data || [];

  return (
    <>
      <Table columns={columns} dataSource={dataSource} rowKey="_id" />
      <Drawer
        title="Vulnerability Details"
        placement="right"
        width={600}
        onClose={closeDrawer}
        visible={drawerVisible}
        headerStyle={{ backgroundColor: "#113032", color: "#fff", borderTopRightRadius: "8px", borderTopLeftRadius: "8px" }}
        bodyStyle={{ backgroundColor: "#113032", padding: "24px", color: "#fff", borderBottomRightRadius: "8px", borderBottomLeftRadius: "8px" }}
        style={{ borderRadius: "8px" }}
      >
        {drawerData && (
          <>
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "30vh" }}>
              <Card
                style={{
                  width: 500,
                  backgroundColor: "#113032",
                  borderColor: "#fff",
                  // borderRadius: "8px",
                  padding: "8px",
                }}
                bodyStyle={{ padding: "0" }}
              >
                <Descriptions
                  bordered
                  column={1}
                  labelStyle={{ color: "#fff", fontWeight: "bold" }}
                  contentStyle={{ color: "#fff" }}
                  style={{ backgroundColor: "#113032", borderColor: "#444" }}
                >
                  <Descriptions.Item label="Package Name">
                    <Tag color="grey" style={{ color: "#fff", borderRadius: "2px" }}>
                      {drawerData.pkg_name || "N/A"}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="Vulnerability ID">
                    <Tag color="red" style={{ color: "red", borderRadius: "2px" }}>
                      {drawerData.vulnerabilityid || "N/A"}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="Severity">
                    <Badge
                      count={drawerData.severity || "N/A"}
                      style={{
                        backgroundColor: getRiskTagColor(drawerData.severity),
                        color: "#fff",
                        padding: "0 12px",
                        borderRadius: "8px",
                        fontWeight: "bold",
                      }}
                    />
                  </Descriptions.Item>
                  <Descriptions.Item label="Status">
                    <Badge
                      status={drawerData.status === "fixed" ? "success" : "error"}
                      text={drawerData.status.toUpperCase() || "N/A"}
                      style={{ color: "#fff", fontWeight: "bold" }}
                    />
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </div>
            <Title level={4} style={{ color: "#fff" }}>{drawerData?.title}</Title>

            <Tabs
              defaultActiveKey="1"
              style={{ backgroundColor: "#113032", color: "#fff" }}
              tabBarStyle={{ color: "#fff" }} // Style for all tab labels
              tabBarGutter={32} // Adds spacing between tabs for a cleaner look
            >
              <Tabs.TabPane
                tab={<span style={{ color: "#fff" }}>Issue Detail</span>}
                key="1"
              >
                <Card
                  style={{
                    backgroundColor: "#1f1f1f",
                    borderColor: "#333",
                    borderRadius: "8px",
                  }}
                  bodyStyle={{ padding: "24px" }}
                >
                  <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                    {/* Title */}
                    <Title level={4} style={{ color: "#fff", marginBottom: "0" }}>
                      Issue Detail
                    </Title>

                    {/* Description with Collapse */}
                    <Collapse
                      bordered={false}
                      expandIcon={({ isActive }) => (
                        <CaretRightOutlined rotate={isActive ? 90 : 0} style={{ color: "#1890ff" }} />
                      )}
                      style={{ backgroundColor: "transparent" }}
                    >
                      <Panel
                        header={
                          <Text strong style={{ color: "white", fontSize: "16px" }}>
                            View Description
                          </Text>
                        }
                        key="1"
                        style={{ border: "none" }}
                      >
                        <Text style={{ color: "#fff", fontSize: "14px", lineHeight: "1.6" }}>
                          {drawerData.description || "No description available."}
                        </Text>
                      </Panel>
                    </Collapse>
                  </Space>
                </Card>
              </Tabs.TabPane>
              <Tabs.TabPane
                tab={<span style={{ color: "#fff" }}>Package Info</span>}
                key="2"
              >
                <Card
                  style={{
                    backgroundColor: "#1f1f1f",
                    borderColor: "#333",
                    borderRadius: "8px",
                  }}
                  bodyStyle={{ padding: "24px" }}
                >
                  <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                    {/* Package Name */}
                    <div>
                      <Text strong style={{ color: "#fff", fontSize: "16px" }}>
                        Package Name:
                      </Text>
                      <Tag
                        color="grey"
                        style={{
                          color: "#fff",
                          borderRadius: "4px",
                          marginLeft: "8px",
                          fontSize: "14px",
                        }}
                      >
                        {drawerData?.pkg_name || "N/A"}
                      </Tag>
                    </div>

                    <Divider style={{ borderColor: "#444", margin: "12px 0" }} />

                    {/* Package ID */}
                    <div>
                      <Text strong style={{ color: "#fff", fontSize: "16px" }}>
                        Package ID:
                      </Text>
                      <Tag
                        color="grey"
                        style={{
                          color: "#fff",
                          borderRadius: "4px",
                          marginLeft: "8px",
                          fontSize: "14px",
                        }}
                      >
                        {drawerData?.pkgid || "N/A"}
                      </Tag>
                    </div>

                    <Divider style={{ borderColor: "#444", margin: "12px 0" }} />

                    {/* Package Identifier (PURL) */}
                    <div>
                      <Text strong style={{ color: "#fff", fontSize: "16px" }}>
                        Package Identifier (PURL):
                      </Text>
                      <Text
                        code
                        style={{
                          color: "lightgreen",
                          marginLeft: "8px",
                          fontSize: "14px",
                        }}
                      >
                        {drawerData?.pkg_identifier?.PURL || "N/A"}
                      </Text>
                    </div>

                    <Divider style={{ borderColor: "#444", margin: "12px 0" }} />

                    {/* Source */}
                    <div>
                      <Text strong style={{ color: "#fff", fontSize: "16px" }}>
                        Source:
                      </Text>
                      <Text
                        style={{
                          color: "#1890ff",
                          marginLeft: "8px",
                          fontSize: "14px",
                        }}
                      >
                        {drawerData?.data_source?.Name || "N/A"}
                      </Text>
                    </div>
                  </Space>
                </Card>
              </Tabs.TabPane>
              <Tabs.TabPane
                tab={<span style={{ color: "#fff" }}>Advisory</span>}
                key="3"
              >
                <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                  {/* <Title level={4} style={{ color: "#fff" }}>Advisory:</Title> */}
                  <div
                    style={{
                      backgroundColor: "white",
                      padding: "24px",
                      borderRadius: "8px",
                      textAlign: "center",
                      border: "1px solid #333",
                    }}
                  >
                    <Title level={3} style={{ color: "black", marginBottom: "8px" }}>
                      Advisory Details
                    </Title>
                    <Text type="secondary" style={{ color: "#aaa", marginBottom: "16px" }}>
                      For more information, click the button below.
                    </Text>
                    <Button
                      type="primary"
                      size="large"
                      icon={<LinkOutlined />}
                      href={drawerData?.data_source?.URL || "N/A"}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Advisory
                    </Button>
                  </div>
                </Space>
              </Tabs.TabPane>
              <Tabs.TabPane
                tab={
                  <span style={{ color: "#fff" }}>Affected Versions</span>
                }
                key="4"
              >
                <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                  {/* <Title level={4} style={{ color: "#fff" }}>Version Comparison:</Title> */}

                  {/* Combined Row for Installed and Fixed Versions */}
                  <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                    {/* Installed Version Card */}
                    <Card
                      style={{ backgroundColor: "white", border: "1px solid #444", flex: 1 }}
                      bodyStyle={{ padding: "16px" }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                        <CodeOutlined style={{ color: "#1890ff", fontSize: "24px" }} />
                        <div>
                          <Title level={5} style={{ color: "black", margin: 0 }}>Installed Version:</Title>
                          <Tag color="red" style={{ color: "red", borderRadius: "4px", marginTop: "8px" }}>
                            {drawerData.installed_version || "N/A"}
                          </Tag>
                        </div>
                      </div>
                    </Card>

                    {/* Arrow Icon */}
                    <ArrowRightOutlined style={{ color: "#fff", fontSize: "24px" }} />

                    {/* Fixed Version Card */}
                    <Card
                      style={{ backgroundColor: "white", border: "1px solid #444", flex: 1 }}
                      bodyStyle={{ padding: "16px" }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                        <CheckCircleOutlined style={{ color: "#52c41a", fontSize: "24px" }} />
                        <div>
                          <Title level={5} style={{ color: "black", margin: 0 }}>Fixed Version:</Title>
                          <Tag color="green" style={{ color: "green", borderRadius: "4px", marginTop: "8px" }}>
                            {drawerData.fixed_version || "N/A"}
                          </Tag>
                        </div>
                      </div>
                    </Card>
                  </div>
                </Space>
              </Tabs.TabPane>


              <Tabs.TabPane
                tab={<span style={{ color: "#fff" }}>References</span>}
                key="5"
              >
                <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                  <Title level={4} style={{ color: "#fff" }}>References:</Title>
                  <Row gutter={[16, 16]}>
                    {drawerData.references ? JSON.parse(drawerData.references).map((ref, index) => (
                      <Col key={index} xs={24} sm={12} md={8} lg={6}>
                        <Card
                          hoverable
                          style={{
                            backgroundColor: "#1f1f1f",
                            borderColor: "#333",
                            borderRadius: "8px",
                          }}
                          bodyStyle={{ padding: "16px", textAlign: "center" }}
                        >
                          <LinkOutlined style={{ fontSize: "24px", color: "#1890ff", marginBottom: "12px" }} />
                          <Title level={5} style={{ color: "#fff", marginBottom: "8px" }}>
                            Reference {index + 1}
                          </Title>
                          <a
                            href={ref}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: "#1890ff", textDecoration: "none" }}
                          >
                            View Reference
                          </a>
                        </Card>
                      </Col>
                    )) : (
                      <Col span={24}>
                        <Text type="secondary" style={{ color: "#aaa", textAlign: "center" }}>
                          No references available.
                        </Text>
                      </Col>
                    )}
                  </Row>
                </Space>
              </Tabs.TabPane>

              {/* <Tabs.TabPane
                tab={
                  <span style={{ color: "#fff" }}>Risk Score</span>
                }
                key="6"
              >
                <Space direction="vertical" size="middle" style={{ width: "100%" }}>
                  <Title level={4} style={{ color: "#fff" }}>Risk Score:</Title>
                  <Tag color={getRiskTagColor(drawerData.severity)} style={{ color: "#fff", borderRadius: "4px" }}>
                    {drawerData.severity || "N/A"}
                  </Tag>
                </Space>
              </Tabs.TabPane> */}
            </Tabs>
          </>
        )}
      </Drawer>
    </>
  );

}

export default SbomVul;

