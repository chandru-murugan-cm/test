import React from "react";
import { Card, Typography, Row, Col, Button } from "antd";
import { useNavigate } from "react-router-dom";
import { DeploymentUnitOutlined, BugOutlined } from "@ant-design/icons";
import { FaShieldAlt } from "react-icons/fa";

const { Title, Text } = Typography;

const complianceData = [
  {
    title: "SAMM (Software Assurance Maturity Model)",
    icon: (
      <DeploymentUnitOutlined style={{ fontSize: "32px", color: "#fff" }} />
    ),
    path: "/frameworks/samm",
    description: "A framework for improving software assurance maturity.",
    color: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    buttonColor: "#667eea", 
  },
  {
    title: "ASVS (Application Security Verification Standard)",
    icon: <FaShieldAlt style={{ fontSize: "32px", color: "#fff" }} />,
    path: "/frameworks/asvs",
    description: "A guide for testing and improving application security.",
    color: "linear-gradient(135deg, #43cea2 0%, #185a9d 100%)",
    buttonColor: "#185a9d", 
  },
  {
    title: "OWASP Top Ten",
    icon: <BugOutlined style={{ fontSize: "32px", color: "#fff" }} />,
    path: "/frameworks/owasp-top-ten",
    description:
      "The top ten most critical security risks in web applications.",
    color: "linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%)",
    buttonColor: "#ff758c", 
  },
];

function Frameworks() {
  const navigate = useNavigate();

  return (
    <div style={{ padding: "0 24px" }}>
      <Title level={3} style={{ color: "#001529", marginBottom: "24px" }}>
        Frameworks
      </Title>
      <Row gutter={[16, 24]} justify="center">
        {complianceData.map((item, index) => (
          <Col xs={24} key={index}>
            <Card
              hoverable
              style={{
                borderRadius: "16px",
                background: "#fff",
                transition: "transform 0.3s ease",
                boxShadow: "0px 4px 15px rgba(0,0,0,0.1)",
                width: "100%",
                maxWidth: "800px",
                overflow: "hidden",
              }}
              bodyStyle={{ padding: "20px" }}
              onClick={() => navigate(item.path)}
            >
              <Row align="middle" justify="space-between">
                {/* Left Section (Icon + Text) */}
                <Col>
                  <Row align="middle" gutter={16}>
                    <Col>
                      <div
                        style={{
                          width: "60px",
                          height: "60px",
                          borderRadius: "50%",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          background: item.color,
                          fontSize: "28px",
                        }}
                      >
                        {item.icon}
                      </div>
                    </Col>
                    <Col>
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
                    </Col>
                  </Row>
                </Col>

                {/* Right Section (Explore Button) */}
                <Col flex="none">
                  <Button
                    type="primary"
                    size="middle"
                    ghost
                    style={{
                      borderColor: item.buttonColor,
                      color: item.buttonColor,
                    }}
                  >
                    Explore
                  </Button>
                </Col>
              </Row>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

export default Frameworks;
