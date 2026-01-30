import React from "react";
import { Select } from "antd";

const DateSelector = ({ dates, selectedDate, onChange }) => {
  return (
    <Select
      placeholder="Select Scheduled Date"
      style={{ width: 200 }}
      onChange={onChange}
      value={selectedDate}
    >
      {dates.map((date) => (
        <Select.Option key={date} value={date}>
          {date}
        </Select.Option>
      ))}
    </Select>
  );
};

export default DateSelector;
