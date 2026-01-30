import React, { useEffect, useState } from "react";
import { Typography, Spin } from "antd";
import { useFetchFixRecommendationQuery } from "../../store/api/cyberService/scannerApi";
import Title from "antd/es/typography/Title";
import Paragraph from "antd/es/typography/Paragraph";

const { Text } = Typography;

const FixView = ({ selectedFinding, activeTab }) => {
  const [localData, setLocalData] = useState(null); // State to manage the local data
  const { data, error, isLoading, refetch } = useFetchFixRecommendationQuery(
    selectedFinding?.fix_recommendation_id,
    {
      skip: activeTab !== "3",
    }
  );

  useEffect(() => {
    // Reset local data when selectedFinding changes
    setLocalData(null);
  }, [selectedFinding]);

  useEffect(() => {
    // Update local data once the fetch is complete
    if (data) {
      setLocalData(data?.data?.ai_fix || null);
    }
  }, [data]);

  if (isLoading || !localData) {
    return (
      <div style={{ textAlign: "center", padding: "20px" }}>
        <span style={{ color: "#fff" }}>Loading</span>
        <Spin size="large" style={{ color: "#fff !important" }} />
      </div>
    );
  }

  if (error) {
    return <div>Error loading details.</div>;
  }

  const renderContent = (content) => {
    const lines = content.split("\n");
    const elements = [];

    let isCodeBlock = false;
    let codeLines = [];

    lines.forEach((line, index) => {
      // Handle code blocks
      if (line.startsWith("```")) {
        if (isCodeBlock) {
          elements.push(
            <pre
              key={`code-${index}`}
              style={{
                backgroundColor: "#1e1e2e",
                color: "#bfbfc8",
                padding: "10px",
                borderRadius: "5px",
                overflowX: "auto",
                fontSize: "13px",
                margin: "10px 0",
              }}
            >
              {codeLines.join("\n")}
            </pre>
          );
          codeLines = [];
          isCodeBlock = false;
        } else {
          isCodeBlock = true;
        }
      } else if (isCodeBlock) {
        codeLines.push(line);
      }
      // Handle Titles (###)
      else if (line.startsWith("### ")) {
        elements.push(
          <Title
            level={5}
            key={`title-${index}`}
            style={{
              color: "#fff",
              margin: 0,
              marginBottom: "6px",
              marginTop: "16px",
            }}
          >
            {line.replace("### ", "")}
          </Title>
        );
      }
      // Handle Numbered lists (1. 2. 3.)
      else if (/^\d+\./.test(line)) {
        elements.push(
          <Text
            key={`numbered-${index}`}
            style={{
              color: "#fff",
              fontSize: "13px",
            }}
          >
            {line}
          </Text>
        );
      }
      // Handle Bulleted lists (-)
      else if (line.startsWith("- ")) {
        elements.push(
          <Text
            key={`bullet-${index}`}
            style={{
              color: "#fff",
              fontSize: "13px",
            }}
          >
            {line}
          </Text>
        );
      }
      // Handle normal text with bold or inline code
      else {
        const parts = [];
        let temp = line;

        // Handling bold text (e.g., **bold**)
        let boldMatch;
        while ((boldMatch = temp.match(/\*\*(.*?)\*\*/)) !== null) {
          parts.push(temp.slice(0, boldMatch.index)); // Add text before **bold**
          parts.push(
            <Text strong key={`bold-${index}`} style={{ color: "#fff" }}>
              {boldMatch[1]} {/* The bolded text */}
            </Text>
          );
          temp = temp.slice(boldMatch.index + boldMatch[0].length); // Remaining text after **bold**
        }

        // Handling inline code (e.g., `code`)
        let codeMatch;
        while ((codeMatch = temp.match(/`(.*?)`/)) !== null) {
          parts.push(temp.slice(0, codeMatch.index)); // Add text before inline code
          parts.push(
            <Text
              code
              key={`code-${index}`}
              style={{
                color: "#f1f1f1",
                padding: "2px 4px",
                borderRadius: "3px",
                margin: "0 2px",
              }}
            >
              {codeMatch[1]} {/* The inline code */}
            </Text>
          );
          temp = temp.slice(codeMatch.index + codeMatch[0].length); // Remaining text after inline code
        }

        // Remove ** and * markers completely
        temp = temp.replace(/\*\*/g, "").replace(/\*/g, "");

        // After all markdown replacements, push the remaining part of the line
        parts.push(temp);

        elements.push(
          <Paragraph
            key={`formatted-${index}`}
            style={{ color: "#bfbfc8", fontSize: "13px" }}
          >
            {parts}
          </Paragraph>
        );
      }
    });

    return elements;
  };

  return (
    <div style={{ padding: "20px" }}>
      {localData ? (
        <>{renderContent(localData)}</>
      ) : (
        <Text style={{ color: "#bfbfc8", fontSize: "13px" }}>
          No AI Fix recommendation available.
        </Text>
      )}
    </div>
  );
};

export default FixView;
