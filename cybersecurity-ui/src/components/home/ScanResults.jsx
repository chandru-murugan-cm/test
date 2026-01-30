import { Row, Col } from "antd";
import ResultCard from "./ResultCard";
import LanguagePieChart from "../dashboard/LanguagePieChart";

const ScanResults = ({ scanResults, languageData }) => {
  const excludedKeys = [
    "repo_path",
    "repo_url",
    "status",
    "domain",
    "job_id",
    "linguist",
    "scans_status",
    "created",
    "creator",
  ];
  const keys = Object.keys(scanResults || {}).filter(
    (key) => !excludedKeys.includes(key)
  );

  return (
    <Row gutter={[16, 16]}>
      {keys
        ?.filter((key) => scanResults[key])
        ?.map((key, index) => (
          <Col
            span={12}
            key={index}
            style={{
              display: "flex",
              overflow: "scroll",
            }}
          >
            <ResultCard title={key} data={scanResults[key]} />
          </Col>
        ))}

      {languageData && (
        <Col span={12} style={{ display: "flex" }}>
          <LanguagePieChart data={languageData} />
        </Col>
      )}
    </Row>
  );
};

export default ScanResults;
