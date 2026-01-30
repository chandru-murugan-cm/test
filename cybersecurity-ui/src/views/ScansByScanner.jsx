import React, { useEffect, useState } from "react";
import ScansByScanner from "../components/scans/ScanByScanner";
import { useParams } from "react-router-dom";
import createAxiosInstance from "../util/axiosInstance";

const ProjectScans = () => {
  const { scannerId } = useParams();
  const [allScans, setAllScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const axiosInstance = createAxiosInstance("cyber-service");

  useEffect(() => {
    const fetchScans = async () => {
      try {
        const response = await axiosInstance.get(
          `/cs/unformatted_scan/scheduler/${scannerId}`
        );

        setAllScans(response?.data?.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchScans();
  }, []);

  if (loading) {
    return <div>Loading scans...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  const scannerSpecificScans = [
    {
      key: "1",
      scanId: 1,
      status: "Success",
      time: "2024-10-10",
      high: 5,
      medium: 3,
      low: 2,
      totalFindings: 10,
    },
    {
      key: "2",
      scanId: 2,
      status: "Failed",
      time: "2024-10-09",
      high: 1,
      medium: 2,
      low: 2,
      totalFindings: 5,
    },
    {
      key: "3",
      scanId: 3,
      status: "In Progress",
      time: "2024-10-08",
      high: 0,
      medium: 0,
      low: 0,
      totalFindings: 0,
    },
  ];

  return (
    <ScansByScanner
      showProjectColumn={false}
      scans={scannerSpecificScans}
      title="Scans for Scanner 1"
    />
  );
};

export default ProjectScans;
