import { Table, Spin, Button, Drawer } from "antd";
import { PlusOutlined, EyeOutlined } from "@ant-design/icons"; // Removed Popover import
import moment from "moment";
import {
  useFetchScannersQuery,
  useFetchScansByProjectQuery,
} from "../../store/api/cyberService/scannerApi";
import ScanNowModal from "./ScanNowModal";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";

const Scans = ({}) => {
  const [isScanNowModalOpen, setIsScanNowModalOpen] = useState(false);
  const [selectedScanners, setSelectedScanners] = useState([]);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [drawerScanTypes, setDrawerScanTypes] = useState([]);
  const { data: scanners } = useFetchScannersQuery();
  const selectedProject = useSelector((state) => state.auth.selectedProject);
  const projectId = selectedProject?._id;
  const {
    data: scanResults,
    isLoading,
    error,
    refetch,
  } = useFetchScansByProjectQuery(projectId, {
    skip: !projectId,
  });

  useEffect(() => {
    if (projectId) {
      refetch();
    }
  }, [projectId, refetch]);

  const unformattedScanResult =
    scanResults?.data
      .map((scan) => ({
        scanId: scan.unformatted_scan_results_id,
        projectName: scan.project_name,
        status: scan.status,
        scanTypes: scan?.scanner_type_details?.join(", "),
        startTime: new Date(scan.created),
        endTime: scan?.updated,
      }))
      .sort((a, b) => b.startTime - a.startTime) || [];

  const formattedScanResult = unformattedScanResult.map((scan) => ({
    ...scan,
    startTime: scan.startTime.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    }),
    endTime: scan?.endTime
      ? new Date(scan?.endTime)?.toLocaleString("en-US", {
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: true,
        })
      : "-",
  }));

  const columns = [
    {
      title: "Start Time",
      dataIndex: "startTime",
      key: "startTime",
      width: 200,
      align: "center",
    },
    {
      title: "End Time",
      dataIndex: "endTime",
      key: "endTime",
      width: 200,
      align: "center",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 150,
      align: "center",
      render: (text) => (
        <span style={{ textTransform: "capitalize" }}>{text}</span>
      ),
    },
    {
      title: "Scan Types",
      dataIndex: "scanTypes",
      key: "scanTypes",
      width: 200,
      align: "center",
      render: (text) => {
        const scanners = text?.split(", ");
        const displayScanners = scanners?.slice(0, 2).join(", ");
        const moreScanners = scanners?.length > 2 ? "..." : "";

        const handleIconClick = () => {
          setDrawerScanTypes(scanners);
          setIsScanNowModalOpen(true);
          // setDrawerVisible(true);
        };

        return (
          <span>
            {/* {displayScanners} */}

            <EyeOutlined
              style={{
                marginLeft: 5,
                cursor: "pointer",
                color: "#6BE992",
              }}
              onClick={handleIconClick}
            />
          </span>
        );
      },
    },
  ].filter(Boolean);

  const handleDrawerClose = () => {
    setDrawerVisible(false);
    setDrawerScanTypes(null);
  };

  return (
    <div style={{ padding: "0px" }}>
      <div style={{ textAlign: "right", marginBottom: "16px" }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setDrawerScanTypes(null);
            setIsScanNowModalOpen(true);
          }}
          style={{ background: "#6BE992", boxShadow: "none" }}
        >
          Scan Now
        </Button>
      </div>
      {isLoading ? (
        <Spin />
      ) : (
        <Table
          columns={columns}
          dataSource={formattedScanResult}
          rowKey="scanId"
          bordered
          style={{ backgroundColor: "#fff", borderRadius: "8px" }}
          size="middle"
          pagination={false}
        />
      )}
      <ScanNowModal
        isScanNowModalOpen={isScanNowModalOpen}
        setIsScanNowModalOpen={setIsScanNowModalOpen}
        selectedProjectId={selectedProject?._id}
        scanners={scanners?.data}
        selectedScanners={selectedScanners}
        setSelectedScanners={setSelectedScanners}
        refetch={refetch}
        drawerScanTypes={drawerScanTypes}
      />
    </div>
  );
};

export default Scans;
