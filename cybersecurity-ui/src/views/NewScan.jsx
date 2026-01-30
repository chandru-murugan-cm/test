import React, { useState } from "react";
import { Form, message } from "antd";
import ScanResults from "../components/home/ScanResults";
import ProgressBar from "../components/home/ProgressBar";
import ScanForm from "../components/Home/ScanForm";
import { useSelector } from "react-redux";
import createAxiosInstance from "../util/axiosInstance";

const predefinedColors = [
  "#FF6384",
  "#36A2EB",
  "#FFCE56",
  "#4BC0C0",
  "#9966FF",
  "#FF9F40",
  "#F7464A",
  "#46BFBD",
  "#FDB45C",
  "#949FB1",
];

const NewScan = () => {
  const [languageData, setLanguageData] = useState(null);
  const [scanResults, setScanResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progressPercentage, setProgressPercentage] = useState(0);
  const [showProgressBar, setShowProgressBar] = useState(false);
  const [form] = Form.useForm();
  const token = useSelector((state) => state.auth.token);
  const axiosInstance = createAxiosInstance("cyber-service");

  const showToast = (type, messageText) => {
    if (type === "success") {
      message.success(messageText, 3);
    } else if (type === "error") {
      message.error(messageText, 3);
    }
  };

  const onFinish = async (values) => {
    setProgressPercentage(0);
    setShowProgressBar(true);
    setLoading(true);
    try {
      const response = await axiosInstance.post("/cs/scan", {
        domain: values.websiteUrl,
        repo_url: values.githubUrl,
      });

      const result = response.data;
      pollScanResults(result.job_id);
    } catch (error) {
      showToast("error", "Error fetching scan results: " + error.message);
      setLoading(false);
      setShowProgressBar(false);
    }
  };

  const pollScanResults = (id) => {
    const interval = setInterval(async () => {
      try {
        const response = await axiosInstance.get(
          `/cs/scan/status?job_id=${id}`
        );
        const result = response.data;
        setScanResults(result);

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
        const [completed, total] = result?.scans_status
          ?.split("/")
          ?.map(Number);
        const progress = ((completed / total) * 100).toFixed(1);
        setProgressPercentage(progress);

        if (result?.status === "completed") {
          clearInterval(interval);
          setLoading(false);
          setShowProgressBar(false);
          showToast("success", "Scan completed successfully!");
        }
      } catch (error) {
        clearInterval(interval);
        showToast("error", "Error polling scan results: " + error.message);
        setLoading(false);
        setShowProgressBar(false);
      }
    }, 3000);
  };

  const handleReset = () => {
    form.resetFields();
    setScanResults(null);
    setLanguageData(null);
    setProgressPercentage(0);
  };

  return (
    <div style={{ padding: "20px", position: "relative" }}>
      <ScanForm
        onFinish={onFinish}
        loading={loading}
        handleReset={handleReset}
        form={form}
      />

      {showProgressBar && (
        <ProgressBar
          progressPercentage={progressPercentage}
          loading={loading}
        />
      )}

      <ScanResults scanResults={scanResults} languageData={languageData} />
    </div>
  );
};

export default NewScan;
