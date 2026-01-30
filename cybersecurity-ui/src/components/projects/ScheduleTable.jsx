import React, { useState } from "react";
import { Table, Modal, Button, message } from "antd";
import { EyeOutlined, PlusOutlined } from "@ant-design/icons";
import moment from "moment";
import ScheduleScannerModal from "./ScheduleScannerModal"; // Adjust the import path
import createAxiosInstance from "../../util/axiosInstance";
import { useFetchScannersQuery } from "../../store/api/cyberService/scannerApi";
import { useDeleteScheduleMutation } from "../../store/api/cyberService/scheduleApi";

const ScheduleTable = ({ schedules, project_id }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [scheduleOption, setScheduleOption] = useState("");
  const [loading, setLoading] = useState(false);
  const [drawerScanTypes, setDrawerScanTypes] = useState([]);
  const [modalMode, setModalMode] = useState("add");
  const axiosInstance = createAxiosInstance("cyber-service");
  const { data: scanners } = useFetchScannersQuery();
  const [deleteSchedule, { isLoading: isDeleting }] =
    useDeleteScheduleMutation();

  const calculateNextScanDate = (scheduleDate, frequency) => {
    const currentTime = moment();
    let nextScanDate = moment(scheduleDate);

    if (frequency === "daily" || frequency === "Daily") {
      while (nextScanDate.isBefore(currentTime)) {
        nextScanDate.add(1, "day");
      }
    } else if (frequency === "weekly") {
      while (nextScanDate.isBefore(currentTime)) {
        nextScanDate.add(7, "days");
      }
    } else if (frequency === "monthly") {
      while (nextScanDate.isBefore(currentTime)) {
        nextScanDate.add(1, "month");
      }
    }

    return nextScanDate.format("YYYY-MM-DD HH:mm:ss");
  };

  const handleAddSchedule = () => {
    setModalMode("add");
    setSelectedSchedule(null);
    setIsModalOpen(true);
    setDrawerScanTypes(null);
  };

  const filteredSchedules = schedules?.filter(
    (schedule) => schedule.options !== "scanNow"
  );

  const columns = [
    {
      title: "S.No",
      dataIndex: "serial",
      key: "serial",
      render: (_, __, index) => index + 1,
      width: "8%",
      align: "center",
    },
    {
      title: "Scheduled Date",
      dataIndex: "next_run",
      key: "next_run",
      render: (date) => (
        <div style={{ padding: "10px 0" }}>
          <span style={{ fontSize: "14px" }}>
            {moment(date).format("MMM D, YYYY hh:mm A")}
          </span>
        </div>
      ),
      width: "25%",
    },
    {
      title: "Next Scan Date",
      dataIndex: "next_scan_time",
      key: "next_scan_time",
      render: (date) => (
        <div style={{ padding: "10px 0" }}>
          <span style={{ fontSize: "14px" }}>
            {moment(date).format("MMM D, YYYY hh:mm A")}
          </span>
        </div>
      ),
      width: "25%",
    },
    {
      title: "Options",
      dataIndex: "options",
      key: "options",
      render: (text) => {
        return text ? text.charAt(0).toUpperCase() + text.slice(1) : "";
      },
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (text) =>
        text ? text.charAt(0).toUpperCase() + text.slice(1) : "",
    },

    {
      title: "Scan Types",
      dataIndex: "scanner_type_details",
      key: "scanTypes",
      width: 150,

      render: (text) => {
        const scanners = text?.map((item) => item?.scan_type);
        const handleIconClick = () => {
          setDrawerScanTypes(scanners);
          setIsModalOpen(true);
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
  ];

  return (
    <>
      <div style={{ textAlign: "right", marginBottom: "16px" }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAddSchedule}
          style={{ background: "#6BE992", boxShadow: "none" }}
        >
          Add Schedule
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={filteredSchedules || []}
        style={{ cursor: "pointer", color: "#1890ff" }}
        pagination={false}
        bordered
      />
      <ScheduleScannerModal
        isModalOpen={isModalOpen}
        setIsModalOpen={setIsModalOpen}
        selectedProjectId={project_id}
        scanners={scanners?.data}
        loading={loading}
        setLoading={setLoading}
        schedule={scheduleOption}
        setSchedule={setScheduleOption}
        mode={modalMode}
        existingScheduleData={selectedSchedule}
        drawerScanTypes={drawerScanTypes}
      />
    </>
  );
};

export default ScheduleTable;
