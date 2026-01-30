import React, { useEffect, useState } from "react";
import {
  Modal,
  Form,
  Checkbox,
  Radio,
  Button,
  message,
  Row,
  Col,
  TimePicker,
  Select,
  Tabs,
  Table,
} from "antd";
import _ from "lodash";
import {
  useAddScheduleMutation,
  useEditScheduleMutation,
} from "../../store/api/cyberService/scheduleApi";
import { useFetchScannerTypesQuery } from "../../store/api/cyberService/scannerApi";
import moment from "moment";

const { TabPane } = Tabs;

const ScheduleScannerModal = ({
  isModalOpen,
  setIsModalOpen,
  selectedProjectId,
  scanners,
  schedule,
  setSchedule,
  mode,
  existingScheduleData,
  drawerScanTypes,
}) => {
  const [form] = Form.useForm();
  const [uniqueTypes, setUniqueTypes] = useState([]);
  const [addSchedule, { isLoading }] = useAddScheduleMutation();
  const [editSchedule, { isLoading: isEditing }] = useEditScheduleMutation();

  const [selectedDay, setSelectedDay] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [selectedScannersByGroup, setSelectedScannersByGroup] = useState({});
  const [selectAllStatus, setSelectAllStatus] = useState({});

  const { data } = useFetchScannerTypesQuery();
  const scannerTypes = data?.data || [];

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

  // Extract unique types from scanners and update state
  useEffect(() => {
    const allTypes = scanners?.flatMap((scanner) => scanner.type);
    const uniqueTypesArray = _.uniq(allTypes);
    setUniqueTypes(uniqueTypesArray);

    if (mode !== "add" && existingScheduleData) {
      // Pre-fill form data in edit/view mode
      form.setFieldsValue({
        scanners: existingScheduleData.scanner_names_list,
        schedule: existingScheduleData.options,
        day: existingScheduleData.day,
        date: existingScheduleData.date,
        time: existingScheduleData.time
          ? moment(existingScheduleData.time, "HH:mm")
          : null, // Convert time to moment object
      });

      setSchedule(existingScheduleData.options);
      setSelectedDay(existingScheduleData.day || null);
      setSelectedDate(existingScheduleData.date || null);
      setSelectedTime(
        existingScheduleData.time
          ? moment(existingScheduleData.time, "HH:mm")
          : null
      );
    } else if (mode === "add") {
      form.resetFields();
      setSelectedDay(null);
      setSelectedDate(null);
      setSelectedTime(null);
      setSchedule("");
    }
  }, [scanners, existingScheduleData, form, mode]);

  const handleScannerChange = (targetType, checkedValues) => {
    setSelectedScannersByGroup((prev) => ({
      ...prev,
      [targetType]: checkedValues,
    }));
  };

  const handleScheduleChange = (e) => {
    setSchedule(e.target.value);
    // Reset specific fields when the schedule changes
    setSelectedDay(null);
    setSelectedDate(null);
    setSelectedTime(null);
  };

  const handleDayChange = (value) => setSelectedDay(value);
  const handleDateChange = (value) => setSelectedDate(value);
  const handleTimeChange = (time) => {
    setSelectedTime(time);
    form.setFieldsValue({ time: time });
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

  const onFinishSchedule = async () => {
    const selectedScanners = Object.values(selectedScannersByGroup).flat();
    if (selectedScanners.length === 0) {
      message.error("Please select at least one scanner!");
      return;
    }
    const currentDate = new Date().toISOString();
    const time = form.getFieldValue("time");

    try {
      const requestBody = {
        project_id: selectedProjectId,
        scheduler_id: existingScheduleData?._id,
        scanner_type_ids_list: selectedScanners,
        options: schedule,
        status: "init",
        schedule_date: currentDate,
        day: selectedDay,
        date: selectedDate,
        time: time ? time?.format("HH:mm") : null,
      };

      console.log(selectedTime?.format("HH:mm"), "time");

      if (mode === "edit") {
        // Call API to update the existing schedule
        await editSchedule({
          id: existingScheduleData._id,
          scheduleData: requestBody,
        }).unwrap();

        message.success("Schedule updated successfully");
      } else {
        // Call API to create a new schedule
        await addSchedule(requestBody).unwrap();
        message.success("Scan scheduled successfully");
      }

      // Reset form fields
      form.resetFields();
      setSchedule("");
      setSelectedDay(null);
      setSelectedDate(null);
      setSelectedTime(null);
      setIsModalOpen(false);
    } catch (error) {
      message.error(
        `Error ${mode === "edit" ? "updating" : "scheduling"} scan`
      );
      console.log(error, "err");
    }
  };

  const onFinishScanNow = async () => {
    const selectedScanners = Object.values(selectedScannersByGroup).flat();
    if (selectedScanners.length === 0) {
      message.error("Please select at least one scanner!");
      return;
    }

    const currentDate = new Date().toISOString();

    try {
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
      setIsModalOpen(false);
      // setIsScanNowModalOpen(false);
    } catch (error) {
      message.error("Error starting scan");
    }
  };
  console.log(drawerScanTypes, "draw");
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
    console.log("filteredData", filteredData);

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
      </>
    );
  };

  return (
    <Modal
      title={
        <span style={{ fontSize: "20px", fontWeight: "bold" }}>
          {drawerScanTypes ? "Selected Scan Types" : "Schedule Scan"}
        </span>
      }
      open={isModalOpen}
      onCancel={() => setIsModalOpen(false)}
      footer={null} // No footer for view mode
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
          ?.map((targetType, index) => (
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
      <Form form={form} onFinish={onFinishSchedule} layout="vertical">
        {!drawerScanTypes && (
          <Form.Item
            label="Select Schedule"
            name="schedule"
            rules={[
              {
                required: mode !== "view",
                message: "Please select a schedule option!",
              },
            ]}
          >
            <Radio.Group
              onChange={handleScheduleChange}
              value={schedule}
              className="custom-radio"
              disabled={mode === "view"} // Disable in view mode
            >
              <Radio.Button value="daily">Daily</Radio.Button>
              {/* <Radio.Button value="weekly">Weekly</Radio.Button>
            <Radio.Button value="monthly">Monthly</Radio.Button> */}
            </Radio.Group>
          </Form.Item>
        )}

        {!drawerScanTypes && schedule && (
          <Form.Item label="Schedule Details" style={{ marginBottom: "-2px" }}>
            <Row gutter={16}>
              {schedule === "daily" && (
                <Col span={8}>
                  <Form.Item
                    label="Time"
                    name="time"
                    rules={[{ required: true, message: "Please select time!" }]}
                  >
                    <TimePicker
                      value={selectedTime}
                      onChange={handleTimeChange}
                      format="HH:mm"
                      disabled={mode === "view"}
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                </Col>
              )}

              {schedule === "weekly" && (
                <>
                  <Col span={8}>
                    <Form.Item
                      label="Day"
                      name="day"
                      rules={[
                        { required: true, message: "Please select a day!" },
                      ]}
                    >
                      <Select
                        value={selectedDay}
                        onChange={handleDayChange}
                        disabled={mode === "view"}
                        style={{ width: "100%" }}
                      >
                        <Select.Option value="Monday">Monday</Select.Option>
                        <Select.Option value="Tuesday">Tuesday</Select.Option>
                        <Select.Option value="Wednesday">
                          Wednesday
                        </Select.Option>
                        <Select.Option value="Thursday">Thursday</Select.Option>
                        <Select.Option value="Friday">Friday</Select.Option>
                        <Select.Option value="Saturday">Saturday</Select.Option>
                        <Select.Option value="Sunday">Sunday</Select.Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      label="Time"
                      name="time"
                      rules={[
                        { required: true, message: "Please select time!" },
                      ]}
                    >
                      <TimePicker
                        value={selectedTime}
                        onChange={handleTimeChange}
                        format="HH:mm"
                        disabled={mode === "view"}
                        style={{ width: "100%" }}
                      />
                    </Form.Item>
                  </Col>
                </>
              )}

              {schedule === "monthly" && (
                <>
                  <Col span={8}>
                    <Form.Item
                      label="Date"
                      name="date"
                      rules={[
                        { required: true, message: "Please select a date!" },
                      ]}
                    >
                      <Select
                        value={selectedDate}
                        onChange={handleDateChange}
                        disabled={mode === "view"}
                        style={{ width: "100%" }}
                      >
                        {[...Array(31).keys()].map((date) => (
                          <Select.Option key={date + 1} value={date + 1}>
                            {date + 1}
                          </Select.Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      label="Time"
                      name="time"
                      rules={[
                        { required: true, message: "Please select time!" },
                      ]}
                    >
                      <TimePicker
                        value={selectedTime}
                        onChange={handleTimeChange}
                        format="HH:mm"
                        disabled={mode === "view"}
                        style={{ width: "100%" }}
                      />
                    </Form.Item>
                  </Col>
                </>
              )}
            </Row>
          </Form.Item>
        )}

        {!drawerScanTypes && (
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={isLoading}
              style={{
                width: "100px",
                background: "#6BE992",
                boxShadow: "none",
              }}
            >
              {mode === "edit" ? "Update" : "Submit"}
            </Button>
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
};

export default ScheduleScannerModal;
