import React from "react";
import { Collapse, Typography, List } from "antd";

const { Panel } = Collapse;
const { Text } = Typography;

function OwaspFramework({ data }) {
  if (!data || !data.data) return <div>No data available</div>;

  // Group items by control_name
  const groupedData = data.data.reduce((acc, item) => {
    if (!acc[item.control_name]) {
      acc[item.control_name] = [];
    }
    acc[item.control_name].push(item);
    return acc;
  }, {});

  return (
    <div style={{ margin: "0 auto" }}>
      <Collapse accordion bordered={false}>
        {Object.entries(groupedData).map(([controlName, items]) => (
          <Panel
            key={controlName}
            header={<Text style={{ fontSize: "16px" }}>{controlName}</Text>}
            style={{
              borderRadius: "4px",
              marginBottom: "8px",
              border: "1px solid #e0e0e0",
              backgroundColor: "#ffffff",
            }}
          >
            <List
              size="small"
              bordered
              dataSource={items}
              renderItem={(item) => (
                <List.Item>
                  <div>
                    <Text>{item.group_name}</Text>
                  </div>
                </List.Item>
              )}
            />
          </Panel>
        ))}
      </Collapse>
    </div>
  );
}

export default OwaspFramework;
