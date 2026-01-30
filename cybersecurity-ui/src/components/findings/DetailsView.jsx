import React from "react";
import { Typography, Spin } from "antd";
import { useFetchExtendedFindingDetailsQuery } from "../../store/api/cyberService/scannerApi";

const { Title, Text } = Typography;

const DetailsView = ({ selectedFinding, activeTab }) => {
  const { data, error, isLoading, refetch } =
    useFetchExtendedFindingDetailsQuery(selectedFinding?._id, {
      skip: activeTab !== "2",
    });

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: "20px" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return <div>Error loading details.</div>;
  }

  const extendedDetails = data?.data?.extended_details;
  const findingMaster = data?.data?.finding_master;

  const formatTitle = (title) => {
    // Special handling for keys ending with "id" to format them as "Cwe Id", "Wasc Id", etc.
    if (title.toLowerCase().endsWith("id")) {
      return title
        .replace(/([a-z])([A-Z])/g, "$1 $2") // Add a space before uppercase letters
        .replace(/_/g, " ") // Replace underscores with spaces
        .replace(/\b(\w)/g, (match) => match.toUpperCase()) // Capitalize each word
        .replace(/id$/, " Id"); // Ensure 'id' is displayed as 'Id'
    }
    return title
      .replace(/([a-z])([A-Z])/g, "$1 $2") // Add a space before uppercase letters
      .replace(/_/g, " ") // Replace underscores with spaces
      .replace(/\b(\w)/g, (match) => match.toUpperCase()); // Capitalize each word
  };

  const renderField = (key, value) => {
    if (!value) return null; // Skip rendering if the value is not available

    // If value is a URL, render it as a clickable link
    const isUrl = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i.test(value);
    const renderedValue = isUrl ? (
      <a
        href={value}
        target="_blank"
        rel="noopener noreferrer"
        style={{ color: "#1890ff" }}
      >
        {value}
      </a>
    ) : (
      value
    );

    return (
      <div style={{ marginBottom: "20px" }}>
        <Title
          level={5}
          className="title"
          style={{ color: "#fff", margin: 0, marginBottom: "6px" }}
        >
          {formatTitle(key)}
        </Title>
        <div style={{ display: "flex", alignItems: "center" }}>
          <Text style={{ color: "#bfbfc8", fontSize: "13px" }}>
            {renderedValue}
          </Text>
        </div>
      </div>
    );
  };

  const renderFieldsBasedOnDetailsName = () => {
    const detailsName = findingMaster?.extended_finding_details_name;

    switch (detailsName) {
      case "RepoSmartContractSlither1":
        return (
          <>
            {renderField("issue_type", extendedDetails?.issue_type)}
            {renderField("line_number", extendedDetails?.line_number)}
            {renderField("contract", extendedDetails?.contract)}
            {renderField("function", extendedDetails?.function)}
            {renderField("source_code_snippet", extendedDetails?.source_code_snippet)}
            {renderField("target_host", extendedDetails?.target_host)}
            {renderField("cweid", extendedDetails?.cweid?.join(", "))}
            {renderField("references", extendedDetails?.references)}
          </>
        );

      case "RepositoryTrivy1":
        return (
          <>
            {renderField(
              "uri  - method",
              `${extendedDetails?.uri} ${extendedDetails?.method} ${extendedDetails?.param}`
            )}
            {renderField("evidence", extendedDetails?.evidence)}
            {renderField("otherinfo", extendedDetails?.otherinfo)}
            {renderField("target_host", extendedDetails?.target_host)}
            {renderField("cweid", extendedDetails?.cweid?.join(", "))}
          </>
        );

      case "RepoSecretDetections":
        return (
          <>
            {renderField("secret", extendedDetails?.secret)}
            {renderField("file_name", extendedDetails?.file_name)}
            {renderField("line_number", extendedDetails?.line_number)}
            {renderField("column_number", extendedDetails?.column_number)}
            {renderField("fix_time", extendedDetails?.fix_time)}
            {renderField("references", extendedDetails?.references?.join(", "))}
            {renderField("cweid", extendedDetails?.cweid)}
            {renderField("wascid", extendedDetails?.wascid)}
          </>
        );

      case "DomainZap1":
      case "DomainWapiti1":
        return (
          <>
            {renderField(
              "uri - method",
              `${extendedDetails?.uri} ${extendedDetails?.method} ${extendedDetails?.param}`
            )}
            {renderField("evidence", extendedDetails?.evidence)}
            {renderField("otherinfo", extendedDetails?.otherinfo)}
            {renderField("attack", extendedDetails?.attack)}
            {renderField("confidence", extendedDetails?.confidence)}
            {renderField("cweid", extendedDetails?.cweid)}
            {renderField("wascid", extendedDetails?.wascid)}
            {renderField("target_host", extendedDetails?.target_host)}
            {renderField("target_port", extendedDetails?.target_port)}
            {renderField(
              "ssl_enabled",
              extendedDetails?.ssl_enabled ? "Yes" : "No"
            )}
          </>
        );


      case "CloudCloudSploitAzure1":
        return (
          <>
            {renderField("category", extendedDetails?.category)}
            {renderField("description", extendedDetails?.description)}
            {renderField("message", extendedDetails?.message)}
            {renderField("plugin", extendedDetails?.plugin)}
            {renderField("region", extendedDetails?.region)}
            {renderField("resource", extendedDetails?.resource)}
            {renderField("status", extendedDetails?.status)}
          </>
        );
      case "CloudCloudSploitGoogle1":
        return (
          <>
            {renderField("category", extendedDetails?.category)}
            {renderField("description", extendedDetails?.description)}
            {renderField("message", extendedDetails?.message)}
            {renderField("plugin", extendedDetails?.plugin)}
            {renderField("region", extendedDetails?.region)}
            {renderField("resource", extendedDetails?.resource)}
            {renderField("status", extendedDetails?.status)}
          </>
        );

      default:
        return <div>No details available for this finding.</div>;
    }
  };

  return (
    <div style={{ padding: "20px" }}>{renderFieldsBasedOnDetailsName()}</div>
  );
};

export default DetailsView;
