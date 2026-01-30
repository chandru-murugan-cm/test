import React, { useState, useEffect } from "react";
import {
  Modal,
  Form,
  Checkbox,
  Button,
  Row,
  Col,
  Tooltip,
  message,
  Tabs,
  Table,
} from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";
import { useAddScheduleMutation } from "../../store/api/cyberService/scheduleApi";
import { useFetchScannerTypesQuery } from "../../store/api/cyberService/scannerApi";

const { TabPane } = Tabs;

const ScanNowModal = ({
  isScanNowModalOpen,
  setIsScanNowModalOpen,
  selectedProjectId,
  refetch,
  drawerScanTypes,
}) => {
  const [form] = Form.useForm();
  const [addSchedule, { isLoading }] = useAddScheduleMutation();
  const { data } = useFetchScannerTypesQuery();
  const scannerTypes = data?.data || [];

  const [selectedScannersByGroup, setSelectedScannersByGroup] = useState({});
  const [selectAllStatus, setSelectAllStatus] = useState({});

  console.log(data, drawerScanTypes, "drawerScanTypes");

  // Group scanners by scan_target_type
  const groupedData = scannerTypes.reduce((acc, item) => {
    const { scan_target_type, scan_type, description, _id } = item;

    if (!acc[scan_target_type]) {
      acc[scan_target_type] = [];
    }

    acc[scan_target_type].push({ scan_type, description, _id });

    return acc;
  }, {});

  useEffect(() => {
    // Reset selected scanners when drawerScanTypes is provided
    if (drawerScanTypes) {
      setSelectedScannersByGroup({});
    }
  }, [drawerScanTypes]);

  const handleScannerChange = (targetType, checkedValues) => {
    setSelectedScannersByGroup((prev) => ({
      ...prev,
      [targetType]: checkedValues,
    }));
  };

  const handleSelectAll = (targetType) => {
    const allValues = groupedData[targetType].map(({ _id }) => _id);
    const isCurrentlySelected = selectAllStatus[targetType] === "all";
    const updatedSelectAllStatus = isCurrentlySelected ? "none" : "all"; // Toggle between "none" and "all"

    setSelectAllStatus((prev) => ({
      ...prev,
      [targetType]: updatedSelectAllStatus,
    }));

    setSelectedScannersByGroup((prev) => ({
      ...prev,
      [targetType]: updatedSelectAllStatus === "all" ? allValues : [],
    }));
  };

  /**
   * Handles submission of scans request
   */
  const onFinishScanNow = async () => {
    // Retrieve all of the selected scanners
    const selectedScanners = Object.values(selectedScannersByGroup).flat();

    // Check that there is at least a scanner selected
    // If that is not the case, display error message and prevent function progress
    if (selectedScanners.length === 0) {
      message.error("Please select at least one scanner!");
      return;
    }

    // Retrieve the current date
    const currentDate = new Date().toISOString();

    try {
      // Create the request body
      const requestBody = {
        project_id: selectedProjectId,
        scanner_type_ids_list: selectedScanners,
        options: "scanNow",
        status: "init",
        time: "00:00",
        schedule_date: currentDate,
      };

      // Call API to create a new schedule
      await addSchedule(requestBody).unwrap();
      message.success("Scan started successfully");
      await refetch();

      // Reset form and state
      form.resetFields();
      setSelectedScannersByGroup({});
      setIsScanNowModalOpen(false);
    } catch (error) {
      message.error("Error starting scan");
    }
  };

  const renderTableColumns = (targetType) => [
    // Conditionally render the checkbox column only if drawerScanTypes is not provided
    ...(drawerScanTypes
      ? []
      : [
          {
            title: "Select",
            dataIndex: "checkbox",
            render: (_, record) => (
              <Checkbox
                value={record._id}
                onChange={(e) =>
                  handleScannerChange(
                    targetType,
                    e.target.checked
                      ? [
                          ...(selectedScannersByGroup[targetType] || []),
                          record._id,
                        ]
                      : selectedScannersByGroup[targetType].filter(
                          (id) => id !== record._id
                        )
                  )
                }
                checked={selectedScannersByGroup[targetType]?.includes(
                  record._id
                )}
              />
            ),
          },
        ]),
    {
      title: "Scan Type",
      dataIndex: "scan_type",
      render: (text, record) => (
        <div
          style={{
            wordWrap: "break-word",
            whiteSpace: "wrap",
            fontSize: "14px",
            padding: "10px 14px",
          }}
        >
          {text}
          <div
            style={{
              marginTop: 5,
              color: "#888",
              whiteSpace: "wrap",
              fontSize: "13px",
            }}
          >
            {record.description}
          </div>
        </div>
      ),
      onCell: () => ({
        style: {
          padding: "10px 14px",
          height: "100%",
        },
      }),
    },
  ];

  const renderTabContent = (targetType) => {
    // Filter the scan types based on drawerScanTypes if it's provided
    const filteredData = drawerScanTypes
      ? groupedData[targetType].filter(({ scan_type }) =>
          drawerScanTypes.includes(scan_type)
        )
      : groupedData[targetType];

    return (
      <>
        {!drawerScanTypes && (
          <Button
            onClick={() => handleSelectAll(targetType)}
            style={{
              background: "#6BE992",
              boxShadow: "none",
              marginBottom: "12px",
              color: "#fff",
            }}
          >
            {selectAllStatus[targetType] === "all"
              ? "Deselect All"
              : "Select All"}
          </Button>
        )}
        <Table
          rowKey="_id"
          columns={renderTableColumns(targetType)}
          dataSource={filteredData}
          pagination={false}
          bordered
        />
        {!drawerScanTypes && (
          <Button
            type="primary"
            onClick={() => onFinishScanNow()}
            loading={isLoading}
            style={{
              marginTop: "20px",
              background: "#6BE992",
              boxShadow: "none",
              width: "100%",
              padding: "20px",
            }}
          >
            Scan Now
          </Button>
        )}
      </>
    );
  };
  console.log(groupedData, "grou");
  return (
    <Modal
      title={
        <span style={{ fontSize: "20px", fontWeight: "bold" }}>
          {drawerScanTypes ? "Selected Scan Types" : "Scan Now"}
        </span>
      }
      open={isScanNowModalOpen}
      onCancel={() => setIsScanNowModalOpen(false)}
      footer={null}
      width={800}
    >
      <Tabs defaultActiveKey="1" type="card">
        {Object.keys(groupedData)
          .filter((targetType) => {
            const filteredData = drawerScanTypes
              ? groupedData[targetType].filter(({ scan_type }) =>
                  drawerScanTypes.includes(scan_type)
                )
              : groupedData[targetType];
            return filteredData.length > 0;
          })
          .map((targetType, index) => (
            <TabPane
              tab={`${
                targetType.charAt(0).toUpperCase() +
                targetType.slice(1).toLowerCase()
              } Scan`}
              key={index}
            >
              {renderTabContent(targetType)}
            </TabPane>
          ))}
      </Tabs>
    </Modal>
  );
};

export default ScanNowModal;
