import React, { useState, useEffect } from "react";
import {
  Tabs,
  Card,
  Collapse,
  Spin,
  Alert,
  Divider,
  Radio,
  Tooltip,
  Row,
  Col,
  Typography,
  Progress,
  Tag,
} from "antd";
import {
  InfoCircleOutlined,
  StarFilled,
  CheckCircleFilled,
  RiseOutlined,
} from "@ant-design/icons";
import { useFetchSammQuery } from "../../store/api/cyberService/sammApi";
import {
  useFetchScoresQuery,
  useAddOrUpdateScoreMutation,
} from "../../store/api/cyberService/sammScoreApi";
import { useSelector } from "react-redux";

const { TabPane } = Tabs;
const { Panel } = Collapse;
const { Title, Text } = Typography;

const themeColor = "rgb(17, 48, 50)"; // Your theme color

export const calculateScoreFromFindings = (findings) => {
  const severityCounts = findings.reduce(
    (acc, finding) => {
      acc[finding.severity] = (acc[finding.severity] || 0) + 1;
      return acc;
    },
    { critical: 0, high: 0, medium: 0, low: 0, info: 0 }
  );

  if (severityCounts.critical > 0) {
    return 0.25;
  } else if (severityCounts.high > 0) {
    return 0.5;
  } else if (severityCounts.medium > 0) {
    return 0.75;
  } else if (severityCounts.low > 0 || severityCounts.info > 0) {
    return 1.0;
  } else {
    return 1.0;
  }
};

// Function to map score to text
const mapScoreToText = (score) => {
  if (score === 0.25) return "None (0.25)";
  if (score === 0.5) return "Some (0.5)";
  if (score === 0.75) return "Half (0.75)";
  if (score === 1) return "Most/All (1)";
  return "Unknown";
};

const TabbedView = ({ onAverageScoreCalculated }) => {
  const [activeTab, setActiveTab] = useState("0");
  const [selectedScores, setSelectedScores] = useState({});
  const [averageScore, setAverageScore] = useState(0);
  const [maxScore, setMaxScore] = useState(0);

  const selectedProject = useSelector((state) => state.auth.selectedProject);

  const { data, error, isLoading } = useFetchSammQuery(
    {
      projectId: selectedProject?._id,
    },
    { skip: !selectedProject?._id }
  );
  const {
    data: scoresData,
    isLoading: scoresLoading,
    error: scoresError,
  } = useFetchScoresQuery(
    { projectId: selectedProject?._id },
    { skip: !selectedProject?._id }
  );

  const [addOrUpdateScore] = useAddOrUpdateScoreMutation();

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

  const calculateTabAverageScore = (l1Key) => {
    const l2Keys = Object.keys(groupedData[l1Key]);
    const totalScore = l2Keys.reduce((total, l2Key) => {
      return total + calculateTotalScore(`${l1Key}-${l2Key}`);
    }, 0);

    return l2Keys.length > 0 ? (totalScore / l2Keys.length).toFixed(1) : 0;
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

      setAverageScore(average);
      setMaxScore(max);
      onAverageScoreCalculated(average);
    }
  }, [groupedData, scoresData]);

  if (isLoading || scoresLoading) {
    return <Spin tip="Loading..." />;
  }

  if (error || scoresError) {
    return <Alert message="Failed to fetch data" type="error" />;
  }

  const handleScoreChange = async (questionKey, score, sammId) => {
    setSelectedScores((prevScores) => ({
      ...prevScores,
      [questionKey]: score,
    }));

    try {
      await addOrUpdateScore({
        samm_id: sammId,
        project_id: selectedProject?._id,
        score,
      }).unwrap();
    } catch (err) {
      console.error("Failed to update score:", err);
    }
  };

  const renderAllL1Scores = () => {
    return (
      groupedData &&
      Object.keys(groupedData)?.map((l1Key) => {
        const l2Keys = Object.keys(groupedData[l1Key]);
        const averageScore = calculateTabAverageScore(l1Key);
        const maxScore =
          l2Keys.reduce((total, l2Key) => {
            return total + calculateMaxScoreForL2(l1Key, l2Key);
          }, 0) / l2Keys?.length;

        return (
          <Col flex="1" key={l1Key}>
            <Card
              title={
                <span style={{ color: "#333" }}>
                  <CheckCircleFilled
                    style={{ color: "#52c41a", marginRight: 8 }}
                  />
                  {l1Key}
                </span>
              }
              bordered={false}
              headStyle={{ backgroundColor: "#f0f0f0", borderBottom: 0 }}
              style={{
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
                borderRadius: 8,
                backgroundColor: "#fff",
              }}
            >
              <Title level={2} style={{ margin: 0, color: "#333" }}>
                {averageScore}
                <span style={{ fontSize: "0.75em" }}>
                  /{maxScore.toFixed(1)}
                </span>
              </Title>
              <Text type="secondary">Average Score </Text>
              <Progress
                percent={parseFloat(
                  ((averageScore / maxScore) * 100).toFixed(1)
                )} // Fixed to 1 decimal place
                status="active"
                strokeColor="#52c41a"
                style={{ marginTop: 16 }}
              />
            </Card>
          </Col>
        );
      })
    );
  };

  return (
    <>
      <Row
        gutter={[16, 16]}
        style={{ marginBottom: 24, flexWrap: "nowrap", marginTop: "15px" }}
      >
        <Col flex="1">
          <Card
            title={
              <span style={{ color: "#333" }}>
                <StarFilled style={{ color: "#ffc53d", marginRight: 8 }} />
                Overall Average Score
              </span>
            }
            bordered={false}
            headStyle={{ backgroundColor: "#f0f0f0", borderBottom: 0 }}
            style={{
              boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              borderRadius: 8,
              backgroundColor: "#fff",
            }}
          >
            <Title level={2} style={{ margin: 0, color: "#333" }}>
              {averageScore}
              <span style={{ fontSize: "0.75em" }}>/{maxScore}</span>
            </Title>
            <Text type="secondary">Average Score</Text>
            <Progress
              percent={parseFloat(((averageScore / maxScore) * 100).toFixed(1))} // Fixed to 1 decimal place
              status="active"
              strokeColor="#52c41a"
              style={{ marginTop: 16 }}
            />
          </Card>
        </Col>
        {renderAllL1Scores()}
      </Row>

      <Tabs activeKey={activeTab} onChange={(key) => setActiveTab(key)}>
        {groupedData &&
          Object.keys(groupedData).map((l1Key, index) => (
            <TabPane tab={l1Key} key={index}>
              <Collapse
                defaultActiveKey={Object.keys(groupedData[l1Key])}
                style={{ marginBottom: 12 }}
              >
                {Object.keys(groupedData[l1Key]).map((l2Key) => (
                  <Panel
                    header={
                      <Row justify="space-between">
                        <Col>{l2Key}</Col>
                        <Col>
                          Section Score:{" "}
                          {calculateTotalScore(`${l1Key}-${l2Key}`).toFixed(1)}/
                          {calculateMaxScoreForL2(l1Key, l2Key).toFixed(1)}{" "}
                          {/* Fixed to 1 decimal place */}
                        </Col>
                      </Row>
                    }
                    key={l2Key}
                  >
                    <Collapse
                      defaultActiveKey={Object.keys(groupedData[l1Key][l2Key])}
                      style={{ marginBottom: 12 }}
                    >
                      {Object.keys(groupedData[l1Key][l2Key]).map((l3Key) => (
                        <Panel
                          header={
                            <Row justify="space-between">
                              <Col>{l3Key}</Col>
                              <Col>
                                Section Score:{" "}
                                {calculateTotalScore(
                                  `${l1Key}-${l2Key}-${l3Key}`
                                ).toFixed(1)}
                                /
                                {groupedData[l1Key][l2Key][
                                  l3Key
                                ]?.length.toFixed(1)}{" "}
                                {/* Fixed to 1 decimal place */}
                              </Col>
                            </Row>
                          }
                          key={l3Key}
                        >
                          {groupedData[l1Key][l2Key][l3Key].map((item, idx) => {
                            const isAutomatedScore =
                              item.matched_findings?.length > 0;
                            const scoreKey = `${l1Key}-${l2Key}-${l3Key}-${item.l4_strategy_and_metrics}`;
                            const scoreValue =
                              selectedScores[scoreKey]?.toFixed(1) || 0;

                            return (
                              <Collapse key={idx} style={{ marginBottom: 12 }}>
                                <Panel
                                  header={
                                    <Row justify="space-between" align="middle">
                                      <Col>{item.l4_strategy_and_metrics}</Col>
                                      <Col>
                                        {isAutomatedScore ? (
                                          <Tag color="green">
                                            Automated Score:{" "}
                                            {calculateScoreFromFindings(
                                              item.matched_findings
                                            )}{" "}
                                            /1.0
                                          </Tag>
                                        ) : selectedScores[scoreKey] ? (
                                          <Tag color="blue">
                                            Score: {scoreValue}/1.0
                                          </Tag>
                                        ) : (
                                          <Tag color="orange">
                                            Manual Evaluation Needed
                                          </Tag>
                                        )}
                                      </Col>
                                    </Row>
                                  }
                                  key="strategy"
                                >
                                  <div style={{ padding: "8px 0" }}>
                                    <Row justify="space-between" align="middle">
                                      <Col>
                                        <p>
                                          <strong>Question:</strong>{" "}
                                          {
                                            item.l4_strategy_and_metrics_question
                                          }
                                          <Tooltip
                                            title={
                                              item.l4_strategy_and_metrics_description
                                            }
                                          >
                                            <InfoCircleOutlined
                                              style={{ marginLeft: 8 }}
                                            />
                                          </Tooltip>
                                        </p>
                                      </Col>
                                    </Row>
                                  </div>
                                  {isAutomatedScore ? (
                                    <div>
                                      <Text strong>Automated Score:</Text>{" "}
                                      {mapScoreToText(
                                        calculateScoreFromFindings(
                                          item.matched_findings
                                        )
                                      )}
                                    </div>
                                  ) : (
                                    item.l4_strategy_and_metrics_coverage
                                      ?.length > 0 && (
                                      <Radio.Group
                                        value={
                                          selectedScores[
                                            `${l1Key}-${l2Key}-${l3Key}-${item.l4_strategy_and_metrics}`
                                          ] || null
                                        }
                                        onChange={(e) =>
                                          handleScoreChange(
                                            scoreKey,
                                            e.target.value,
                                            item._id
                                          )
                                        }
                                      >
                                        {item.l4_strategy_and_metrics_coverage.map(
                                          (coverage) => (
                                            <div
                                              key={coverage.coverage_name}
                                              style={{ marginBottom: 12 }}
                                            >
                                              <Radio
                                                value={coverage.coverage_score}
                                              >
                                                {coverage.coverage_name}
                                                <Tooltip
                                                  title={
                                                    coverage.coverage_description
                                                  }
                                                >
                                                  <InfoCircleOutlined
                                                    style={{ marginLeft: 8 }}
                                                  />
                                                </Tooltip>
                                              </Radio>
                                            </div>
                                          )
                                        )}
                                      </Radio.Group>
                                    )
                                  )}
                                </Panel>
                              </Collapse>
                            );
                          })}
                        </Panel>
                      ))}
                    </Collapse>
                  </Panel>
                ))}
              </Collapse>
            </TabPane>
          ))}
      </Tabs>
    </>
  );
};

export default TabbedView;
