import React, { useState, useEffect } from "react";
import { Typography, Spin } from "antd";
import { useNavigate } from "react-router-dom";
import ProjectTable from "../components/projects/ProjectTable";
import ScheduleScannerModal from "../components/projects/ScheduleScannerModal";
import ScanNowModal from "../components/projects/ScanNowModal";
import { useFetchProjectsQuery } from "../store/api/cyberService/projectApi";
import { useFetchScannersQuery } from "../store/api/cyberService/scannerApi";
import createAxiosInstance from "../util/axiosInstance";

const { Title } = Typography;

const Projects = () => {
  const [selectedScanners, setSelectedScanners] = useState([]);
  const [schedule, setSchedule] = useState(null);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isScanNowModalOpen, setIsScanNowModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const axiosInstance = createAxiosInstance("cyber-service");

  const { data: projects, isLoading: projectsLoading } =
    useFetchProjectsQuery();
  const { data: scanners } = useFetchScannersQuery();

  const navigate = useNavigate();

  const handleScanNow = (projectId) => {
    setSelectedProjectId(projectId);
    setIsScanNowModalOpen(true);
  };

  const handleScheduleScanner = (projectId) => {
    setSelectedProjectId(projectId);
    setIsModalOpen(true);
  };

  return (
    <div style={{ padding: "24px" }}>
      <Title level={4} style={{ margin: 0, marginBottom: "15px" }}>
        Projects
      </Title>

      {projectsLoading ? (
        <Spin tip="Loading projects..." size="large">
          <div style={{ minHeight: "200px" }}></div>
        </Spin>
      ) : (
        <ProjectTable
          projects={projects?.data}
          navigate={navigate}
          handleScanNow={handleScanNow}
          handleScheduleScanner={handleScheduleScanner}
        />
      )}

      <ScheduleScannerModal
        isModalOpen={isModalOpen}
        setIsModalOpen={setIsModalOpen}
        selectedProjectId={selectedProjectId}
        scanners={scanners?.data}
        loading={loading}
        setLoading={setLoading}
        schedule={schedule}
        setSchedule={setSchedule}
        selectedScanners={selectedScanners}
        setSelectedScanners={setSelectedScanners}
        axiosInstance={axiosInstance}
      />

      <ScanNowModal
        isScanNowModalOpen={isScanNowModalOpen}
        setIsScanNowModalOpen={setIsScanNowModalOpen}
        selectedProjectId={selectedProjectId}
        scanners={scanners?.data}
        loading={loading}
        setLoading={setLoading}
        selectedScanners={selectedScanners}
        setSelectedScanners={setSelectedScanners}
        axiosInstance={axiosInstance}
      />
    </div>
  );
};

export default Projects;
