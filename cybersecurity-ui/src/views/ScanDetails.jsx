import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ScanResults from "../components/home/ScanResults";
import ProgressBar from "../components/home/ProgressBar";
import createAxiosInstance from "../util/axiosInstance";

const predefinedColors = [
  "#FF6384",
  "#36A2EB",
  "#FFCE56",
  "#4BC0C0",
  "#9966FF",
  "#FF9F40",
  "#FF4F00",
  "#4BFF00",
  "#00FFC5",
  // Add more colors as needed
];

const ScanDetails = () => {
  const { id } = useParams(); // Get scan ID from URL
  const [scanResults, setScanResults] = useState(null);
  const [languageData, setLanguageData] = useState({
    labels: [],
    datasets: [],
  });
  const [progressPercentage, setProgressPercentage] = useState(0);
  const [showProgressBar, setShowProgressBar] = useState(false);

  useEffect(() => {
    const fetchScanData = async () => {
      try {
        const axiosInstance = createAxiosInstance("cyber-service");
        const response = await axiosInstance.get(`/scan/status?job_id=${id}`);
        const result = response.data;
        setScanResults(result);

        // Check if scan is pending
        if (result?.status === "pending") {
          setShowProgressBar(true);
          pollScanResults(id); // Poll scan results if scan is still pending
        }

        const linguistData =
          result?.linguist?.split("\n")?.filter((item) => item.trim() !== "") ||
          [];

        const labels = linguistData.map((item) => {
          const parts = item.trim().split(/\s+/);
          return parts.slice(-1)[0].replace(/[()]/g, "");
        });

        const data = linguistData.map((item) => {
          const parts = item.trim().split(/\s+/);
          return parseFloat(parts.slice(0, -1).join(" "));
        });

        const updatedData = {
          labels: labels,
          datasets: [
            {
              data: data,
              backgroundColor: predefinedColors.slice(0, data.length),
              hoverBackgroundColor: predefinedColors.slice(0, data.length),
            },
          ],
        };

        setLanguageData(updatedData);
      } catch (error) {
        console.error("Error fetching scan details:", error);
      }
    };

    fetchScanData();
  }, [id]); // Run effect when id changes

  const pollScanResults = (scanId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axiosInstance.get(
          `/scan/status?job_id=${scanId}`
        );
        const result = response.data;
        setScanResults(result);

        const [completed, total] = result?.scans_status
          ?.split("/")
          ?.map(Number);
        const progress = ((completed / total) * 100).toFixed(1);
        setProgressPercentage(progress);

        // Stop polling when scan is completed
        if (result?.status === "completed") {
          clearInterval(interval);
          setShowProgressBar(false);
        }
      } catch (error) {
        clearInterval(interval);
        console.error("Error polling scan results:", error);
        setShowProgressBar(false);
      }
    }, 3000); // Poll every 3 seconds
  };

  // Function to handle report download
  const handleDownloadReport = async () => {
    try {
      const axiosInstance = createAxiosInstance("cyber-service");
      const response = await axiosInstance.get(`/scan/report?job_id=${id}`, {
        responseType: "blob", // Important for downloading files
      });

      // Create a blob link to download the file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `scan_report_${id}.pdf`); // Adjust file name and extension as needed
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error downloading report:", error);
    }
  };

  return (
    <div style={{ position: "relative" }}>
      <h2>Scan Details</h2>
      <p>Showing details for scan ID: {id}</p>

      {/* Download Button */}
      <button
        onClick={handleDownloadReport}
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          padding: "8px 12px",
          backgroundColor: "rgb(0,33,64)",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Download Report
      </button>

      {showProgressBar && (
        <ProgressBar progressPercentage={progressPercentage} />
      )}

      {/* Render ScanResults component with fetched data */}
      <ScanResults scanResults={scanResults} languageData={languageData} />
    </div>
  );
};

export default ScanDetails;
