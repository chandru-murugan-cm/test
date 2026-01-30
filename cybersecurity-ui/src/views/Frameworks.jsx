import React, { useState } from "react";
import { Card, Typography, Row, Col, Button, Progress } from "antd";
import { useNavigate } from "react-router-dom";
import { DeploymentUnitOutlined, BugOutlined } from "@ant-design/icons";
import { FaShieldAlt } from "react-icons/fa";
import { useSelector } from "react-redux";
import { useFetchScoresQuery } from "../store/api/cyberService/sammScoreApi";
import { useFetchSammQuery } from "../store/api/cyberService/sammApi";
import { useEffect } from "react";
import { calculateScoreFromFindings } from "../components/samm/HierarchicalTree ";

const { Title, Text } = Typography;

const complianceData = [
  {
    title: "SAMM (Software Assurance Maturity Model)",
    icon: <DeploymentUnitOutlined />,
    path: "/frameworks/samm",
    description: "A framework for improving software assurance maturity.",
  },
  {
    title: "ASVS (Application Security Verification Standard)",
    icon: <FaShieldAlt />,
    path: "/frameworks/asvs",
    description: "A guide for testing and improving application security.",
  },
  {
    title: "OWASP Top Ten",
    icon: <BugOutlined />,
    path: "/frameworks/owasp-top-ten",
    description:
      "The top ten most critical security risks in web applications.",
  },
];

function Frameworks() {
  const navigate = useNavigate();
  const [selectedScores, setSelectedScores] = useState({});
  const [score, setScore] = useState(0);
  const [maxScore, setMaxScore] = useState(0);

  const selectedProject = useSelector((state) => state.auth.selectedProject);
  const { data, error, isLoading } = useFetchSammQuery({
    projectId: selectedProject?._id,
  });
  const { data: scoresData } = useFetchScoresQuery({
    projectId: selectedProject?._id,
  });

  useEffect(() => {
    if (scoresData?.data) {
      const prepopulatedScores = scoresData.data.reduce((acc, score) => {
        const sammItem = data?.data?.find((item) => item._id === score.samm_id);
        if (sammItem) {
          const key = `${sammItem.l1_business_function}-${sammItem.l2_security_practice}-${sammItem.l3_stream}-${sammItem.l4_strategy_and_metrics}`;
          acc[key] = score.score;
        }
        return acc;
      }, {});

      setSelectedScores(prepopulatedScores);
    }
  }, [scoresData, data, selectedProject]);

  useEffect(() => {
    if (data?.data) {
      const updatedScores = data.data.reduce((acc, sammItem) => {
        if (sammItem.matched_findings?.length > 0) {
          const key = `${sammItem.l1_business_function}-${sammItem.l2_security_practice}-${sammItem.l3_stream}-${sammItem.l4_strategy_and_metrics}`;
          acc[key] = Number(
            calculateScoreFromFindings(sammItem.matched_findings).toFixed(1)
          );
        }
        return acc;
      }, {});

      setSelectedScores((prevScores) => ({ ...prevScores, ...updatedScores }));
    }
  }, [data]);

  const groupedData = data?.data?.reduce((acc, item) => {
    const { l1_business_function, l2_security_practice, l3_stream } = item;

    if (!acc[l1_business_function]) acc[l1_business_function] = {};
    if (!acc[l1_business_function][l2_security_practice]) {
      acc[l1_business_function][l2_security_practice] = {};
    }
    if (!acc[l1_business_function][l2_security_practice][l3_stream]) {
      acc[l1_business_function][l2_security_practice][l3_stream] = [];
    }

    acc[l1_business_function][l2_security_practice][l3_stream].push(item);

    return acc;
  }, {});

  const calculateTotalScore = (sectionKey) => {
    return Object.keys(selectedScores)
      .filter((key) => key.startsWith(sectionKey))
      .reduce((total, key) => total + (selectedScores[key] || 0), 0);
  };

  const calculateTabAverageScore = (l1Key) => {
    const l2Keys = Object.keys(groupedData[l1Key]);
    const totalScore = l2Keys.reduce((total, l2Key) => {
      return total + calculateTotalScore(`${l1Key}-${l2Key}`);
    }, 0);

    return l2Keys.length > 0 ? (totalScore / l2Keys.length).toFixed(1) : 0;
  };

  const calculateMaxScoreForL2 = (l1Key, l2Key) => {
    const l3Keys = Object.keys(groupedData[l1Key][l2Key]);
    return l3Keys.reduce((total, l3Key) => {
      return total + groupedData[l1Key][l2Key][l3Key].length; // Each l4 item has a max score of 1
    }, 0);
  };

  const calculateMaxScoreForL1 = (l1Key) => {
    const l2Keys = Object.keys(groupedData[l1Key]);
    const totalMaxScore = l2Keys.reduce((total, l2Key) => {
      return total + calculateMaxScoreForL2(l1Key, l2Key);
    }, 0);
    return l2Keys.length > 0 ? totalMaxScore / l2Keys.length : 0;
  };

  useEffect(() => {
    if (groupedData) {
      const l1Keys = Object.keys(groupedData);
      const totalScore = l1Keys.reduce(
        (total, l1Key) => total + Number(calculateTabAverageScore(l1Key)),
        0
      );

      const totalMaxScore = l1Keys.reduce(
        (total, l1Key) => total + calculateMaxScoreForL1(l1Key),
        0
      );

      const average =
        l1Keys.length > 0 ? (totalScore / l1Keys.length).toFixed(2) : 0; // Fixed to 1 decimal place
      const max =
        l1Keys.length > 0 ? (totalMaxScore / l1Keys.length).toFixed(1) : 0; // Fixed to 1 decimal place
      setMaxScore(max);
      setScore(average);
    }
  }, [groupedData, scoresData]);

  const handleCardClick = (path) => {
    navigate(path);
  };

  return (
    <div style={{ padding: "0 24px" }}>
      <Title
        level={4}
        style={{ color: "#001529", marginBottom: "15px", marginTop: 0 }}
      >
        Frameworks
      </Title>
      <Row gutter={[16, 24]}>
        {complianceData.map((item, index) => (
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
              onClick={() => handleCardClick(item.path)}
            >
              <Row align="middle" justify="space-between">
                {/* Left Section: Icon and Content */}
                <Col flex="auto">
                  <Row align="middle" gutter={16}>
                    {/* Icon Section */}
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

                    {/* Content Section */}
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

                {/* Right Section: Progress Bar and Score */}
                {index === 0 && ( // Assuming totalScore is only for the first framework
                  <Col
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      minWidth: "120px",
                    }}
                  >
                    <Progress
                      percent={(score / maxScore) * 100}
                      type="circle"
                      width={60}
                      strokeColor="#4CAF50"
                      style={{ marginBottom: "8px" }}
                      format={() => `${score}`}
                    />
                    <Text style={{ fontSize: "14px", color: "#333" }}>
                      Total Score: {score} / {maxScore}
                    </Text>
                  </Col>
                )}
              </Row>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

export default Frameworks;
