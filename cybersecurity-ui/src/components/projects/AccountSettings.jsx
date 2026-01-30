import React, { useState, useEffect } from "react";
import { Typography, Tabs, Row, Col, message, Tag } from "antd";
import WorkspaceInfoCard from "./WorkspaceInfoCard";
import DangerZoneCard from "./DangerZoneCard";
import RepositoriesTab from "./RepositoriesTab";
import DomainTab from "./Domain";
import ContractTab from "./Contract";
import ScannerList from "./ScannerList";
import Scans from "./Scans";
import ScheduleTable from "./ScheduleTable";
import CloudTab from "./Cloud";
import { useFetchSchedulesQuery } from "../../store/api/cyberService/scheduleApi";

const { Title } = Typography;
const { TabPane } = Tabs;

const AccountSettings = ({ projectDetails, refetch }) => {
  const [workspaceName, setWorkspaceName] = useState("");
  const [activeTabKey, setActiveTabKey] = useState("1");

  // Sync state with new projectDetails when it changes
  useEffect(() => {
    if (projectDetails) {
      setWorkspaceName(projectDetails.name || "Untitled Project");
    }
  }, [projectDetails]);

  const {
    data: schedules,
    error: schedulesError,
    isLoading: schedulesLoading,
  } = useFetchSchedulesQuery(projectDetails?._id);

  const handleDomainUpdate = (newDomainDetails) => {
    setDomainDetails(newDomainDetails);
    message.success("Domain details updated.");
  };

  // Handle tab change to trigger actions when a tab is selected
  const handleTabChange = (key) => {
    setActiveTabKey(key);
  };

  return (
    <div style={{ padding: "0 " }}>
      {/* Title Section */}
      <div style={titleStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Title level={3} style={{ margin: 0 }}>
            {workspaceName}
          </Title>
          <Tag color="green">
            {projectDetails?.repo_url_data?.length !== 0
              ? `${projectDetails?.repo_url_data?.length} active repo`
              : "No active repos"}
          </Tag>
        </div>
      </div>

      {/* Tabs Section */}
      <Tabs
        activeKey={activeTabKey} // Controlled active tab state
        onChange={handleTabChange} // Trigger action when tab changes
        style={{ marginTop: "15px" }}
      >
        <TabPane tab="General" key="1">
          <Row gutter={[24, 24]}>
            {/* Workspace Info */}
            <Col xs={24} lg={12}>
              <WorkspaceInfoCard projectDetails={projectDetails} />
              <DangerZoneCard projectDetails={projectDetails} />
            </Col>
          </Row>
        </TabPane>

        <TabPane tab="Repositories" key="2">
          <RepositoriesTab projectDetails={projectDetails} refetch={refetch} />
        </TabPane>
        <TabPane tab="Domains" key="3">
          <DomainTab projectDetails={projectDetails} refetch={refetch} />
        </TabPane>
        <TabPane tab="Web3" key="4">
          <ContractTab projectDetails={projectDetails} refetch={refetch} />
        </TabPane>
        <TabPane tab="Cloud" key="6">
          <CloudTab projectDetails={projectDetails} refetch={refetch} />
        </TabPane>

        <TabPane tab="Schedule" key="5">
          <ScheduleTable
            schedules={Array.isArray(schedules?.data) ? schedules?.data : []}
            project_id={projectDetails?._id}
          />
        </TabPane>
      </Tabs>
    </div>
  );
};

const titleStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

export default AccountSettings;
