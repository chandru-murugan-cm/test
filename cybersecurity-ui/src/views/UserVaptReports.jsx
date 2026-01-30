import React, { useState } from "react";
import { List, Button, message, Spin, Modal } from "antd";
import { DownloadOutlined, EyeOutlined, CloseOutlined } from "@ant-design/icons";
import { useFetchVaptReportsQuery } from "../store/api/cyberService/vaptReportApi";
import { useSelector } from "react-redux";

const UserVaptReports = () => {
    const { user, token, selectedProject } = useSelector((state) => state.auth);
    const { data: reportsData, isLoading, error } = useFetchVaptReportsQuery(
        {
            user_id: user?.userId,
            project_id: selectedProject?._id,
        },
        { skip: !selectedProject?._id }
    );
    const [pdfUrl, setPdfUrl] = useState(null);
    const [viewerVisible, setViewerVisible] = useState(false);
    const [viewingReportName, setViewingReportName] = useState("");

    const fetchReportBlob = async (reportId) => {
        const response = await fetch(
            `${import.meta.env.VITE_API_CYBER_SERVICE_BASE_URL}/crscan/vapt-reports/${reportId}/download`,
            { headers: { Authorization: `Bearer ${token}` } }
        );
        if (!response.ok) throw new Error("Failed to fetch the report.");
        return response;
    };

    const handleView = async (reportId, reportName) => {
        try {
            const response = await fetchReportBlob(reportId);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            setPdfUrl(url);
            setViewingReportName(reportName || "VAPT Report");
            setViewerVisible(true);
        } catch (err) {
            message.error("View failed: " + err.message);
        }
    };

    const handleCloseViewer = () => {
        setViewerVisible(false);
        if (pdfUrl) {
            window.URL.revokeObjectURL(pdfUrl);
            setPdfUrl(null);
        }
        setViewingReportName("");
    };

    const handleDownload = async (reportId, reportName) => {
        try {
            const response = await fetchReportBlob(reportId);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;

            const contentDisposition = response.headers.get("content-disposition");
            let filename = reportName || "download.pdf";
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                if (filenameMatch && filenameMatch.length > 1) {
                    filename = filenameMatch[1];
                }
            }

            a.setAttribute("download", filename);
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            message.error("Download failed: " + err.message);
        }
    };

    if (!selectedProject?._id) {
        return (
            <div style={{ padding: "15px" }}>
                <div style={{ fontSize: "20px", marginBottom: "10px" }}>
                    Your VAPT Reports
                </div>
                <div style={{ textAlign: "center", color: "#888", padding: "40px" }}>
                    Please select a project to view VAPT reports.
                </div>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div style={{ padding: "15px", textAlign: "center" }}>
                <Spin size="large" />
            </div>
        );
    }

    if (error) {
        return <div style={{ padding: "15px" }}>Error fetching reports.</div>;
    }

    return (
        <div style={{ padding: "15px" }}>
            <div style={{ fontSize: "20px", marginBottom: "10px" }}>
                Your VAPT Reports
            </div>
            <List
                itemLayout="horizontal"
                dataSource={reportsData?.data}
                renderItem={(item) => (
                    <List.Item
                        actions={[
                            <Button
                                icon={<EyeOutlined />}
                                onClick={() => handleView(item._id, item.report_name)}
                            >
                                View
                            </Button>,
                            <Button
                                icon={<DownloadOutlined />}
                                onClick={() => handleDownload(item._id, item.report_name)}
                            >
                                Download
                            </Button>,
                        ]}
                    >
                        <List.Item.Meta
                            title={item.report_name}
                            description={`Uploaded on: ${new Date(
                                item.uploaded_at
                            ).toLocaleDateString()}`}
                        />
                    </List.Item>
                )}
            />
            <Modal
                title={viewingReportName}
                open={viewerVisible}
                onCancel={handleCloseViewer}
                footer={null}
                width="90%"
                style={{ top: 20 }}
                styles={{ body: { height: "80vh", padding: 0 } }}
                destroyOnClose
            >
                {pdfUrl && (
                    <iframe
                        src={pdfUrl}
                        style={{
                            width: "100%",
                            height: "100%",
                            border: "none",
                            minHeight: "75vh",
                        }}
                        title="VAPT Report Viewer"
                    />
                )}
            </Modal>
        </div>
    );
};

export default UserVaptReports;
