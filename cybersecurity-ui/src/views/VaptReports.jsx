import React, { useState } from "react";
import { Table, Button, Space, message, Modal } from "antd";
import { DownloadOutlined, EyeOutlined } from "@ant-design/icons";
import { useParams } from "react-router-dom";
import { useFetchVaptReportsQuery } from "../store/api/cyberService/vaptReportApi";
import { useSelector } from "react-redux";

const VaptReports = () => {
    const { projectId } = useParams();
    const { data: vaptReportsData, isLoading } = useFetchVaptReportsQuery({ project_id: projectId });
    const token = useSelector((state) => state.auth.token);
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
        } catch (error) {
            message.error(error.message);
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
            a.href = url;
            const contentDisposition = response.headers.get("content-disposition");
            let filename = reportName;
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?(.+)"?/i);
                if (match) filename = match[1].replace(/"/g, "");
            }
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            message.error(error.message);
        }
    };

    const columns = [
        {
            title: "Report Name",
            dataIndex: "report_name",
            key: "report_name",
        },
        {
            title: "Uploaded At",
            dataIndex: "uploaded_at",
            key: "uploaded_at",
            render: (text) => new Date(text).toLocaleString(),
        },
        {
            title: "Action",
            key: "action",
            render: (_, record) => (
                <Space>
                    <Button
                        icon={<EyeOutlined />}
                        onClick={() => handleView(record._id, record.report_name)}
                    >
                        View
                    </Button>
                    <Button
                        icon={<DownloadOutlined />}
                        onClick={() => handleDownload(record._id, record.report_name)}
                    >
                        Download
                    </Button>
                </Space>
            ),
        },
    ];

    return (
        <div style={{ padding: "15px" }}>
            <div style={{ fontSize: "20px", marginBottom: "10px" }}>
                VAPT Reports
            </div>
            <Table
                columns={columns}
                dataSource={vaptReportsData?.data}
                loading={isLoading}
                rowKey="_id"
                bordered
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

export default VaptReports;
