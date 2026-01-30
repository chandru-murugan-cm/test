import React from "react";
import { Card, Typography, Row, Col, Button, Spin } from "antd";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  FaShieldAlt,
  FaClipboardList,
  FaLock,
  FaFileSignature,
  FaCogs,
} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { useFetchComplianceSummaryQuery } from "../store/api/cyberService/complianceAp";

const { Title, Text } = Typography;

const complianceData = [
  {
    title: "GDPR Compliance",
    icon: <FaShieldAlt />,
    description: "Protect user privacy and comply with GDPR regulations.",
    state: "GDPR Compliance Overview",
  },
  {
    title: "HIPAA Compliance",
    icon: <FaClipboardList />,
    description: "Secure healthcare data by following HIPAA guidelines.",
    state: "HIPAA compliance overview",
  },
  {
    title: "ISO 27001:2022 Compliance",
    icon: <FaLock />,
    description: "Enhance information security with ISO 27001 compliance.",
    state: "ISO 27001:2022 compliance overview",
  },
  {
    title: "NIS2 Compliance",
    icon: <FaFileSignature />,
    description: "Meet NIS2 standards for improved cybersecurity frameworks.",
    state: "NIS2 compliance overview",
  },
  {
    title: "PCI Compliance",
    icon: <FaCogs />,
    description: "Protect payment data with PCI DSS standards.",
    state: "PCI compliance overview",
  },
];

function ComplianceDashboard() {
  const navigate = useNavigate();
  const selectedProject = useSelector((state) => state.auth.selectedProject);

  // Fetch compliance summary only if selectedProject._id exists
  const { data, error, isLoading } = useFetchComplianceSummaryQuery(
    selectedProject?._id,
    {
      skip: !selectedProject?._id,
    }
  );

  const complianceSummary = data?.data || [];

  const handleCardClick = (state) => {
    navigate(`/complianceDetails`, { state: { complianceState: state } });
  };

  return (
    <div style={{ padding: "0 24px" }}>
      <Title
        level={4}
        style={{
          fontWeight: "bold",
          color: "#333",
          marginBottom: "15px",
          marginTop: 0,
        }}
      >
        Compliance
      </Title>

      {isLoading ? (
        <Spin
          size="large"
          style={{ display: "block", textAlign: "center", marginTop: "50px" }}
        />
      ) : error ? (
        <Text type="danger">Failed to load compliance summary.</Text>
      ) : (
        <Row gutter={[16, 24]}>
          {complianceData.map((item, index) => {
            const complianceDetails = complianceSummary.find(
              (c) => c.compliance_type === item.state
            );

            return (
              <Col xs={24} key={index}>
                <Card
                  hoverable
                  style={{
                    borderRadius: "16px",
                    background: "#fff",
                    boxShadow: "0 6px 20px rgba(0,0,0,0.1)",
                    overflow: "hidden",
                    transition: "transform 0.3s ease",
                  }}
                  bodyStyle={{ padding: "0 20px 20px" }}
                  onClick={() => handleCardClick(item.state)}
                >
                  <Row align="middle" justify="space-between">
                    {/* Left Side: Compliance Details */}
                    <Col flex="auto">
                      <Row align="middle" gutter={16}>
                        <Col flex="80px">
                          <div
                            style={{
                              width: "60px",
                              height: "60px",
                              backgroundColor: "#6BE992",
                              borderRadius: "50%",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              color: "#fff",
                              fontSize: "28px",
                            }}
                          >
                            {item.icon}
                          </div>
                        </Col>

                        <Col flex="auto">
                          <Title
                            level={4}
                            style={{ marginBottom: "8px", color: "#333" }}
                          >
                            {item.title}
                          </Title>
                          <Text
                            style={{
                              display: "block",
                              color: "#666",
                              marginBottom: "12px",
                            }}
                          >
                            {item.description}
                          </Text>
                          <Button
                            type="primary"
                            size="middle"
                            style={{
                              boxShadow: "none",
                              backgroundColor: "#6BE992",
                            }}
                          >
                            Explore
                          </Button>
                        </Col>
                      </Row>
                    </Col>

                    {/* Right Side: Compliance Chart with Legend */}
                    {complianceDetails && (
                      <Col style={{ minWidth: "200px", textAlign: "center" }}>
                        <Row align="middle">
                          {/* Legend Information (Only Left Side) */}
                          <Col
                            style={{ textAlign: "left", marginRight: "16px" }}
                          >
                            <div style={{ marginBottom: "8px" }}>
                              <span
                                style={{
                                  display: "inline-block",
                                  width: "12px",
                                  height: "12px",
                                  backgroundColor: "#4CAF50",
                                  marginRight: "8px",
                                }}
                              ></span>
                              <Text style={{ fontSize: "14px", color: "#333" }}>
                                Complying
                              </Text>
                            </div>
                            <div style={{ marginBottom: "8px" }}>
                              <span
                                style={{
                                  display: "inline-block",
                                  width: "12px",
                                  height: "12px",
                                  backgroundColor: "#FFC107",
                                  marginRight: "8px",
                                }}
                              ></span>
                              <Text style={{ fontSize: "14px", color: "#333" }}>
                                Manual Eval Needed
                              </Text>
                            </div>
                            <div>
                              <span
                                style={{
                                  display: "inline-block",
                                  width: "12px",
                                  height: "12px",
                                  backgroundColor: "#F44336",
                                  marginRight: "8px",
                                }}
                              ></span>
                              <Text style={{ fontSize: "14px", color: "#333" }}>
                                Non-Complying
                              </Text>
                            </div>
                          </Col>

                          {/* Bar Chart */}
                          <Col
                            style={{ marginTop: "20px", marginRight: "50px" }}
                          >
                            <ResponsiveContainer width={200} height={150}>
                              <BarChart data={[complianceDetails]}>
                                <XAxis dataKey="compliance_type" hide />
                                <YAxis />
                                <Tooltip />
                                <Bar
                                  dataKey="complying_count"
                                  fill="#4CAF50"
                                  name="Complying"
                                />
                                <Bar
                                  dataKey="manual_evaluation_needed_count"
                                  fill="#FFC107"
                                  name="Manual Eval Needed"
                                />
                                <Bar
                                  dataKey="non_complying_count"
                                  fill="#F44336"
                                  name="Non-Complying"
                                />
                              </BarChart>
                            </ResponsiveContainer>
                          </Col>
                        </Row>
                      </Col>
                    )}
                  </Row>
                </Card>
              </Col>
            );
          })}
        </Row>
      )}
    </div>
  );
}

export default ComplianceDashboard;
