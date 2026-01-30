import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  useCreateManualComplianceEvaluationMutation,
  useFetchCompliancesQuery,
} from "../store/api/cyberService/complianceAp";
import {
  Collapse,
  Typography,
  Spin,
  Tag,
  Select,
  message,
  Card,
  Row,
  Col,
  Statistic,
} from "antd";
import {
  ExclamationCircleOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { useSelector } from "react-redux";
import {
  FaExclamationCircle,
  FaCheckCircle,
  FaSync,
  FaFile,
} from "react-icons/fa";
import { GiNetworkBars } from "react-icons/gi";

const { Panel } = Collapse;
const { Title, Text } = Typography;
const { Option } = Select;

function ComplianceDetails() {
  const location = useLocation();
  const navigate = useNavigate();
  const [createManualCompliance] =
    useCreateManualComplianceEvaluationMutation();

  const { complianceState } = location.state || {};
  const [activeKey, setActiveKey] = useState(null);
  const selectedProject = useSelector((state) => state.auth.selectedProject);

  useEffect(() => {
    if (!complianceState) {
      navigate("/compliance");
    }
  }, [complianceState, navigate]);

  const { data, error, isLoading } = useFetchCompliancesQuery({
    complianceState,
    project_id: selectedProject?._id,
  });

  const handleManualEvaluationChange = async (value, controlId) => {
    const payload = {
      project_id: selectedProject?._id,
      evaluation_status: value,
      compliance_id: controlId,
    };
    try {
      await createManualCompliance(payload).unwrap();
      message.success(`Compliance status updated to ${value}`);
    } catch (err) {
      message.error("Failed to update compliance status");
      console.error(err);
    }
  };

  const getControlGroupStatus = (controls) => {
    let manualNeeded = 0;
    let complying = 0;
    let notComplying = 0;

    controls.forEach((control) => {
      if (control.matchedFindings.length === 0) {
        if (control.manualEvaluation?.length > 0) {
          control.manualEvaluation[0]?.evaluation_status === "complying"
            ? complying++
            : notComplying++;
        } else {
          manualNeeded++;
        }
      } else {
        notComplying++;
      }
    });

    if (manualNeeded > 0) return "manual";
    if (complying === controls.length) return "complying";
    if (notComplying === controls.length) return "not-complying";
    if (complying > 0 && notComplying > 0) return "partial";
    return "not-complying";
  };

  const renderStatusTag = (status) => {
    switch (status) {
      case "manual":
        return <Tag color="blue">Manual Evaluation Needed</Tag>;
      case "complying":
        return <Tag color="green">Complying</Tag>;
      case "not-complying":
        return <Tag color="red">Not Complying</Tag>;
      case "partial":
        return <Tag color="orange">Partially Complying</Tag>;
      default:
        return <Tag color="gray">Unknown Status</Tag>;
    }
  };

  const calculateOverviewData = (complianceData) => {
    let totalControls = 0;
    let totalComplying = 0;
    let totalNotComplying = 0;
    let totalManualNeeded = 0;

    complianceData.forEach((item) => {
      totalControls++;
      if (item.matched_findings.length === 0) {
        if (item.manual_compliance_evaluation?.length > 0) {
          item.manual_compliance_evaluation[0]?.evaluation_status ===
          "complying"
            ? totalComplying++
            : totalNotComplying++;
        } else {
          totalManualNeeded++;
        }
      } else {
        totalNotComplying++;
      }
    });

    return {
      totalControls,
      totalComplying,
      totalNotComplying,
      totalManualNeeded,
    };
  };

  if (isLoading)
    return (
      <div style={{ textAlign: "center", padding: "20px" }}>
        <Spin size="large" />
      </div>
    );

  if (error)
    return <div style={{ textAlign: "center" }}>Error fetching data</div>;

  const complianceData = data?.data || [];
  const groupedData = complianceData.reduce((acc, item) => {
    const {
      compliance_group_name,
      compliance_control_name,
      matched_findings,
      compliance_scanner_mapping,
      manual_compliance_evaluation,
      _id,
    } = item;

    if (!acc[compliance_control_name]) {
      acc[compliance_control_name] = [];
    }

    acc[compliance_control_name].push({
      groupName: compliance_group_name,
      matchedFindings: matched_findings || [],
      scannerTypeId: compliance_scanner_mapping?.scanner_type_id || [],
      controlId: _id,
      manualEvaluation: manual_compliance_evaluation,
    });
    return acc;
  }, {});

  const handlePanelChange = (key) => {
    setActiveKey(key === activeKey ? null : key);
  };

  const calculateSeverityCounts = (matchedFindings) => {
    return matchedFindings.reduce(
      (acc, finding) => {
        const severity = finding.severity?.toLowerCase() || "info";
        acc[severity] = (acc[severity] || 0) + 1;
        return acc;
      },
      { critical: 0, high: 0, medium: 0, low: 0 }
    );
  };

  const handleNavigateToFindings = (scannerTypeId) => {
    const queryParams = new URLSearchParams(location.search);
    queryParams.set("scanTypeIds", scannerTypeId.join(","));
    navigate(`/findings?${queryParams.toString()}`);
  };

  const overviewData = calculateOverviewData(complianceData);

  return (
    <div style={{ padding: "0 24px" }}>
      <Title
        level={4}
        style={{
          marginBottom: "20px",
          marginTop: 0,
          textTransform: "capitalize",
        }}
      >
        {complianceState}
      </Title>

      {/* Overview Section */}
      <Row gutter={[16, 16]} style={{ marginBottom: "24px" }}>
        <Col xs={24} sm={12} md={6}>
          <div
            style={{
              background: "#ffffff",
              borderRadius: "8px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              padding: "16px",
              display: "flex",
              justifyContent: "flex-start",
              gap: "10px",
              alignItems: "center",
              height: "90px",
            }}
          >
            <FaFile size={40} color="#6BE992" />
            <div>
              <Title
                level={5}
                style={{
                  margin: 0,
                  fontSize: "14px",
                  marginBottom: "4px", // Reduced bottom margin
                }}
              >
                Total Controls
              </Title>
              <p
                style={{
                  fontSize: "14px",
                  color: "#8c8c8c",
                  margin: 0, // Removed marginTop
                }}
              >
                {overviewData.totalControls} Items
              </p>
            </div>
          </div>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <div
            style={{
              background: "#ffffff",
              borderRadius: "8px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              padding: "16px",
              display: "flex",
              justifyContent: "flex-start",
              gap: "25px",
              alignItems: "center",
              height: "90px",
            }}
          >
            <FaCheckCircle size={40} color="#6BE992" />
            <div>
              <Title
                level={5}
                style={{
                  margin: 0,
                  fontSize: "14px",
                  marginBottom: "4px",
                }}
              >
                Complying Controls
              </Title>
              <p
                style={{
                  fontSize: "14px",
                  color: "#8c8c8c",
                  margin: 0,
                }}
              >
                {overviewData.totalComplying} Items
              </p>
            </div>
          </div>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <div
            style={{
              background: "#ffffff",
              borderRadius: "8px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              padding: "16px",
              display: "flex",
              justifyContent: "flex-start",
              gap: "25px",
              alignItems: "center",
              height: "90px",
            }}
          >
            <FaExclamationCircle size={40} color="#6BE992" />
            <div>
              <Title
                level={5}
                style={{
                  margin: 0,
                  fontSize: "14px",
                  marginBottom: "4px",
                }}
              >
                Not Complying Controls
              </Title>
              <p
                style={{
                  fontSize: "14px",
                  color: "#8c8c8c",
                  margin: 0,
                }}
              >
                {overviewData.totalNotComplying} Items
              </p>
            </div>
          </div>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <div
            style={{
              background: "#ffffff",
              borderRadius: "8px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              padding: "16px",
              display: "flex",
              justifyContent: "flex-start",
              gap: "25px",
              alignItems: "center",
              height: "90px",
            }}
          >
            <FaSync size={40} color="#6BE992" />
            <div>
              <Title
                level={5}
                style={{
                  margin: 0,
                  fontSize: "14px",
                  marginBottom: "4px",
                }}
              >
                Manual Evaluation Needed
              </Title>
              <p
                style={{
                  fontSize: "14px",
                  color: "#8c8c8c",
                  margin: 0,
                }}
              >
                {overviewData.totalManualNeeded} Items
              </p>
            </div>
          </div>
        </Col>
      </Row>

      <Collapse
        accordion
        activeKey={activeKey}
        onChange={handlePanelChange}
        expandIconPosition="end"
        style={{ background: "transparent", border: "none" }}
      >
        {Object.entries(groupedData).map(([controlName, controls]) => {
          const groupStatus = getControlGroupStatus(controls);

          return (
            <Panel
              header={
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 16,
                    justifyContent: "space-between",
                  }}
                >
                  <Text strong style={{ fontSize: "16px" }}>
                    {controlName}
                  </Text>
                  {renderStatusTag(groupStatus)}
                </div>
              }
              key={controlName}
              style={{
                marginBottom: "10px",
                borderRadius: "8px",
                border: "1px solid #d9d9d9",
                overflow: "hidden",
              }}
            >
              {controls.map((control, index) => {
                const {
                  groupName,
                  matchedFindings,
                  scannerTypeId,
                  controlId,
                  manualEvaluation,
                } = control;
                const severityCounts = calculateSeverityCounts(matchedFindings);

                return (
                  <div
                    key={index}
                    style={{
                      padding: "12px",
                      backgroundColor: "#ffffff",
                      borderBottom:
                        index !== controls.length - 1
                          ? "1px solid #f0f0f0"
                          : "none",
                      display: "flex",
                      justifyContent: "space-between ",
                      alignItems: "center",
                    }}
                  >
                    <Text>{groupName}</Text>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                      {matchedFindings.length === 0 ? (
                        manualEvaluation?.length > 0 ? (
                          manualEvaluation[0]?.evaluation_status ===
                          "complying" ? (
                            <Tag color="green">
                              <CheckCircleOutlined style={{ marginRight: 5 }} />
                              Complying
                            </Tag>
                          ) : (
                            <Tag color="red">
                              <ExclamationCircleOutlined
                                style={{ marginRight: 5 }}
                              />
                              Not Complying
                            </Tag>
                          )
                        ) : (
                          <div
                            style={{ display: "flex", alignItems: "center" }}
                          >
                            <Tag color="blue">Manual Evaluation Needed</Tag>
                            <Select
                              defaultValue=""
                              style={{ width: 150, marginLeft: 10 }}
                              onChange={(value) =>
                                handleManualEvaluationChange(value, controlId)
                              }
                            >
                              <Option value="">Select Status</Option>
                              <Option value="complying">Complying</Option>
                              <Option value="not-complying">
                                Not Complying
                              </Option>
                            </Select>
                          </div>
                        )
                      ) : (
                        <>
                          <div
                            style={{
                              marginRight: "16px",
                              display: "flex",
                              gap: "12px",
                            }}
                          >
                            {Object.entries(severityCounts).map(
                              ([severity, count]) =>
                                count > 0 && (
                                  <Text
                                    key={severity}
                                    style={{
                                      cursor: "pointer",
                                      color: "#1890ff",
                                    }}
                                    onClick={() =>
                                      handleNavigateToFindings(scannerTypeId)
                                    }
                                  >
                                    {severity === "critical" && (
                                      <FaExclamationCircle
                                        style={{ color: "red" }}
                                      />
                                    )}
                                    {severity === "high" && (
                                      <GiNetworkBars
                                        style={{ color: "orange" }}
                                      />
                                    )}
                                    {severity === "medium" && (
                                      <GiNetworkBars
                                        style={{ color: "gold" }}
                                      />
                                    )}
                                    {severity === "low" && (
                                      <GiNetworkBars
                                        style={{ color: "blue" }}
                                      />
                                    )}{" "}
                                    {count}{" "}
                                    {severity.charAt(0).toUpperCase() +
                                      severity.slice(1)}
                                  </Text>
                                )
                            )}
                          </div>
                          <Tag color="red">
                            <FaExclamationCircle style={{ marginRight: 5 }} />
                            Not Complying
                          </Tag>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </Panel>
          );
        })}
      </Collapse>
    </div>
  );
}

export default ComplianceDetails;
