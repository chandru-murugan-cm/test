import { Card } from "antd";
import { CheckCircleOutlined } from "@ant-design/icons";

const ResultCard = ({ title, data }) => {
  return (
    <Card
      title={`${title.charAt(0).toUpperCase() + title.slice(1)} Report`}
      bordered={false}
      style={{ flex: 1, marginBottom: "20px" }}
      headStyle={{ backgroundColor: "#eae8e8" }}
      bodyStyle={{
        overflowY: "auto",
        maxHeight: "300px",
        paddingTop: "8px",
      }}
    >
      {title === "zap" ? (
        <iframe
          srcDoc={data}
          title="OWASP ZAP Report"
          style={{ width: "100%", height: "400px", border: "none" }}
        />
      ) : Array.isArray(data) ? (
        <ul style={{ listStyleType: "none", paddingLeft: 0 }}>
          {data
            ?.filter((item) => item.trim() !== "")
            ?.map((item, idx) => (
              <li
                key={idx}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  marginBottom: "10px",
                }}
              >
                <CheckCircleOutlined
                  style={{
                    color: "green",
                    marginRight: "8px",
                    marginTop: "4px",
                    fontSize: "18px",
                  }}
                />
                {item}
              </li>
            ))}
        </ul>
      ) : (
        <pre>{data}</pre>
      )}
    </Card>
  );
};

export default ResultCard;
