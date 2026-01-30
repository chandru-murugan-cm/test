import React, { useState } from "react";
import {
  Drawer,
  Tabs,
  Tag,
  Button,
  Dropdown,
  Menu,
  Collapse,
  Table,
  Typography,
  Tooltip,
  message,
} from "antd";
import {
  InfoCircleOutlined,
  FieldTimeOutlined,
  ClusterOutlined,
  LinkOutlined,
  CloseOutlined,
  GithubOutlined,
  GlobalOutlined,
  RadarChartOutlined,
  CheckCircleOutlined,
  BulbOutlined,
  CodeOutlined,
  LockOutlined,
  FileSearchOutlined,
  CloudOutlined
} from "@ant-design/icons";
import moment from "moment";
import { useUpdateFindingStatusMutation } from "../../store/api/cyberService/scannerApi";
import DetailsView from "./DetailsView";
import FixView from "./FixView";

// Define color for different severity levels
const severityColors = {
  critical: "red",
  high: "orange",
  medium: "gold",
  low: "green",
};

const { TabPane } = Tabs;
const { Panel } = Collapse;
const { Title, Text } = Typography;

const getScanTypeIcon = (scanType) => {
  const iconMap = {
    "Secrets Detection": <LockOutlined style={{ fontSize: "20px" }} />,
    "Smart Contract Vulnerability Scanner": <ClusterOutlined style={{ fontSize: "20px" }} />,
    "Licenses and SBOM": <FileSearchOutlined style={{ fontSize: "20px" }} />,
    "Dependency Vulnerability Scanner": (
      <CodeOutlined style={{ fontSize: "20px" }} />
    ),
    "Languages and Framework": <CodeOutlined style={{ fontSize: "20px" }} />,
  };

  return (
    iconMap[scanType] || (
      <GlobalOutlined style={{ fontSize: "20px", color: "#6C757D" }} />
    )
  );
};

const FindingDetailsDrawer = ({
  visible,
  onClose,
  selectedFinding,
  setSelectedFinding,
  activeTab,
  setActiveTab,
}) => {
  const target = selectedFinding?.target_id;

  const [updateFindingStatus, { isLoading }] = useUpdateFindingStatusMutation();

  const handleTabChange = (key) => {
    setActiveTab(key);
    if (key === "2") {
      refetch();
    }
  };

  // Check if the target is a GitHub repository or a domain
  const isRepo = target && target.includes("github.com");
  const isContract = target && selectedFinding?.target_type === "web3";
  const isCloud = target && selectedFinding?.target_type === "cloud";

  const tagStyle = {
    fontSize: "12px",
    marginLeft: "10px",
    display: "flex",
    alignItems: "center", // Ensures icon and text are vertically aligned
    justifyContent: "center",
    padding: "2px 8px", // Adds uniform padding for better spacing
    textTransform: "capitalize",
  };

  const getSeverityTag = (
    <Tag color="grey" style={tagStyle}>
      {selectedFinding?.severity}
    </Tag>
  );

  const scannerTag = (
    <Tag color="grey" style={{ ...tagStyle, marginLeft: 0 }}>
      {getScanTypeIcon(selectedFinding?.scan_type_details?.scan_type)}
      {selectedFinding?.scan_type_details?.scan_type || "Unknown Scanner"}
    </Tag>
  );

  const statusTag = (
    <Tag color="grey" style={tagStyle}>
      <CheckCircleOutlined style={{ marginRight: 5 }} />
      {selectedFinding?.status || "Pending"}
    </Tag>
  );

  const getRelativeTime = (time) => moment(time).fromNow();

  const handleMenuClick = ({ key }) => {
    const statusMapping = {
      1: "ignored",
      2: "false positive",
      3: "closed",
    };

    console.log(selectedFinding, "key");

    if (key in statusMapping && selectedFinding?._id) {
      updateFindingStatus({
        findingId: selectedFinding._id,
        status: statusMapping[key],
      })
        .unwrap()
        .then((response) => {
          setSelectedFinding((prev) => ({
            ...prev,
            status: response?.data?.status,
          }));
          message.success("Status updated successfully");
        })
        .catch((err) => {
          console.error("Failed to update status:", err);
        });
    }
  };

  const menu = (
    <Menu>
      <Menu.Item key="1" onClick={handleMenuClick}>
        Ignored
      </Menu.Item>
      <Menu.Item key="2" onClick={handleMenuClick}>
        False Positive
      </Menu.Item>
      <Menu.Item key="3" onClick={handleMenuClick}>
        Closed
      </Menu.Item>
    </Menu>
  );

  return (
    <Drawer
      title={
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {/* Close Button and Action Dropdown in the Top Row */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              width: "100%",
            }}
          >
            {/* Close Button on Left */}
            <Button
              type="text"
              icon={<CloseOutlined />}
              onClick={onClose}
              style={{
                color: "#fff",
                fontSize: "20px",
                padding: "0",
                marginLeft: "10px",
                alignSelf: "flex-start",
              }}
            />

            {/* Action Dropdown Button on Right */}
            <Dropdown overlay={menu} trigger={["click"]}>
              <Button
                style={{
                  background: "#6BE992",
                  boxShadow: "none",
                  color: "#fff",
                  padding: "8px 16px",
                  fontSize: "12px",
                  fontWeight: "500",
                  borderRadius: "6px",
                  marginRight: "10px",
                  transition: "all 0.3s ease-in-out",
                  alignSelf: "flex-start",
                  border: "none",
                }}
                onMouseEnter={(e) =>
                  (e.target.style.backgroundColor = "#6BE992")
                }
                onMouseLeave={(e) =>
                  (e.target.style.backgroundColor = "#6BE992")
                }
              >
                Actions
              </Button>
            </Dropdown>
          </div>
        </div>
      }
      placement="right"
      closable={false}
      onClose={onClose}
      visible={visible}
      width={700}
      style={{
        paddingTop: "10px",
        backgroundColor: "#113032",
        color: "#fff",
        borderRadius: "10px",
      }}
    >
      {selectedFinding && (
        <>
          {/* Issue Info and Severity Row */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              marginBottom: "20px",
              paddingLeft: "10px",
              paddingRight: "10px",
              marginTop: "-12px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                marginRight: "20px",
                backgroundColor:
                  severityColors[selectedFinding?.severity] || "gray",
                borderRadius: "50%",
                width: "100px",
                height: "100px",
                justifyContent: "center",
                textTransform: "capitalize",
                color: "#fff",
                fontWeight: "bold",
                flexShrink: 0,
                minWidth: "100px",
                minHeight: "100px",
              }}
            >
              <span style={{ fontSize: "20px" }}>
                {selectedFinding?.severity === "informational"
                  ? "Info"
                  : selectedFinding?.severity}
              </span>
            </div>

            <div>
              <div
                style={{ fontSize: "18px", fontWeight: "bold", color: "#fff" }}
              >
                {selectedFinding?.findings || "No Title"}
              </div>
              <div style={{ fontSize: "12px", color: "#aaa" }}>
                Reported: {getRelativeTime(selectedFinding?.scanDate)}
              </div>

              <div
                style={{
                  marginTop: "10px",
                  display: "flex",
                  gap: "4px",
                  flexWrap: "wrap",
                }}
              >
                {scannerTag}
                {statusTag}
              </div>
            </div>
          </div>

          {/* Tabs Section */}
          <Tabs
            tabPosition="top"
            style={{
              color: "#fff",
              backgroundColor: "#113032",
              border: "none",
              paddingTop: "10px",
            }}
            activeKey={activeTab}
            onChange={handleTabChange}
          >
            {/* First Tab: Overview */}
            <TabPane
              tab={
                <span style={{ color: "#fff" }}>
                  <InfoCircleOutlined /> Overview
                </span>
              }
              key="1"
              style={{
                padding: "10px",
                background: "transparent",
              }}
            >
              <div style={{ marginBottom: "20px" }}>
                <Title
                  level={5}
                  className="title"
                  style={{ color: "#fff", margin: 0, marginBottom: "6px" }}
                >
                  Target
                </Title>
                <div style={{ display: "flex", alignItems: "center" }}>
                  {/* Conditionally render the icon based on the target */}
                  <Tooltip title={target}>
                  {isRepo ? (
                      <GithubOutlined
                        style={{ marginRight: 8, color: "#fff" }}
                      />
                    ) : isCloud ? (
                      <CloudOutlined
                        style={{ marginRight: 8, color: "#fff" }}
                      />
                    ) : isContract ? (
                      <ClusterOutlined
                        style={{ marginRight: 8, color: "#fff" }}
                      />
                    ) : (
                      <GlobalOutlined
                        style={{ marginRight: 8, color: "#fff" }}
                      />
                    )}
                  </Tooltip>

                  {/* Display the target text */}
                  <Text style={{ color: "#bfbfc8", fontSize: "13px" }}>
                  {
                    isCloud
                      ? selectedFinding?.target_details?.name
                      : isContract
                        ? selectedFinding?.target_details?.contract_label
                        : isRepo
                          ? selectedFinding?.target_details?.repository_url
                          : selectedFinding?.target_details?.domain_url
                  }
                  </Text>
                </div>
              </div>
              <div style={{ marginBottom: "20px" }}>
                <Title
                  level={5}
                  className="title"
                  style={{ color: "#fff", margin: 0, marginBottom: "6px" }}
                >
                  Scan Type
                </Title>
                <div style={{ display: "flex", alignItems: "center" }}>
                  {/* Conditionally render the icon based on the target */}
                  <Tooltip title={target}>
                    <RadarChartOutlined
                      style={{ marginRight: 8, color: "#fff" }}
                    />
                  </Tooltip>

                  {/* Display the target text */}
                  <Text style={{ color: "#bfbfc8", fontSize: "13px" }}>
                    {selectedFinding?.scan_type_details?.scan_type}
                  </Text>
                </div>
              </div>
              <div
                className="white-text-container"
                style={{ marginBottom: "20px" }}
              >
                <Title
                  level={5}
                  className="title"
                  style={{ color: "#fff", margin: 0, marginBottom: "6px" }}
                >
                  Description
                </Title>
                <Text style={{ color: "#bfbfc8", fontSize: "13px" }}>
                  {selectedFinding?.finding_desc}
                </Text>
              </div>
            </TabPane>

            <TabPane
              tab={
                <span style={{ color: "#fff" }}>
                  <FieldTimeOutlined /> Details
                </span>
              }
              key="2"
            >
              <DetailsView
                selectedFinding={selectedFinding}
                activeTab={activeTab}
              />
            </TabPane>

            {/* Second Tab: Notes */}
            <TabPane
              tab={
                <span style={{ color: "#fff" }}>
                  <BulbOutlined style={{ marginRight: "4px" }} />
                  Fix Recommendations
                </span>
              }
              key="3"
            >
              <FixView
                selectedFinding={selectedFinding}
                activeTab={activeTab}
              />
            </TabPane>

            {/* Third Tab: Tasks */}
            {/* <TabPane
              tab={
                <span style={{ color: "#fff" }}>
                  <FileTextOutlined /> Tasks
                </span>
              }
              key="4"
              style={{
                padding: "20px",
                background: "transparent",
              }}
            >
              <div>
                <p style={{ color: "#fff", marginTop: 0 }}>
                  There are no notes yet for this issue. Be the first one to
                  leave one!
                </p>
                <input
                  type="text"
                  placeholder="Leave a plaintext note, no HTML"
                  style={{
                    width: "100%",
                    padding: "10px",
                    borderRadius: "4px",
                    border: "1px solid #555",
                    backgroundColor: "#113032",
                    color: "#fff",
                    marginBottom: "10px",
                  }}
                />
                <button
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#6BE992",
                    border: "none",
                    color: "#fff",
                    borderRadius: "4px",
                  }}
                >
                  Add Note
                </button>
              </div>
            </TabPane> */}
          </Tabs>
        </>
      )}
    </Drawer>
  );
};

export default FindingDetailsDrawer;
