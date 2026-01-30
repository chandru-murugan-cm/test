import React, { useState } from "react";
import { useFetchLicensesByProjectIdQuery } from "../../store/api/cyberService/repoScanResultsApi.js.js";
import { Spin, Alert, Collapse, Typography, Skeleton } from "antd";
import { LoadingOutlined } from "@ant-design/icons";

const { Panel } = Collapse;
const { Text, Title } = Typography;

function Licenses({ project_id }) {
  const {
    data: licensesData,
    error,
    isLoading,
  } = useFetchLicensesByProjectIdQuery(project_id);

  const [licenseDetails, setLicenseDetails] = useState({}); // Store AI-generated details
  const [loadingLicense, setLoadingLicense] = useState(null); // Track which license is loading

  // Handle loading state
  if (isLoading) return <Spin size="large" />;

  // Handle error state
  if (error)
    return (
      <Alert message="Error" description="Error fetching data" type="error" />
    );

  // Check if data exists
  const licenses = licensesData?.data || [];

  // Function to fetch detailed license details from OpenAI
  const fetchLicenseDetails = async (licenseName) => {
    setLoadingLicense(licenseName); // Set loading state
    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer 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`, // Replace with your OpenAI API key
        },
        body: JSON.stringify({
          model: "gpt-3.5-turbo",
          messages: [
            {
              role: "user",
              content: `Provide a detailed and complete description of the ${licenseName} software license. Ensure the following:
                        1. The content must be complete and not truncated or partial.
                        2. The information must be accurate and directly sourced from the official license text or documentation.
                        3. Include the following details:
                          - Purpose of the license
                          - Key permissions (what users are allowed to do)
                          - Key restrictions (what users are not allowed to do)
                          - Key conditions (requirements for using the license)
                          - A direct quote or summary of the official license text, if available.
                        4. Do not provide incomplete or speculative information. If you are unsure, state that the information is unavailable.`,
            },
          ],
          max_tokens: 500, // Increase token limit for detailed content
        }),
      });

      const data = await response.json();
      const details = data.choices[0].message.content.trim();

      // Update license details state
      setLicenseDetails((prev) => ({
        ...prev,
        [licenseName]: details,
      }));
    } catch (err) {
      console.error("Error fetching license details:", err);
      setLicenseDetails((prev) => ({
        ...prev,
        [licenseName]: "Failed to fetch details. Please try again.",
      }));
    } finally {
      setLoadingLicense(null); // Clear loading state
    }
  };

  return (
    <div style={{ marginTop: "10px" }}>
      <Collapse accordion>
        {licenses.map((licenseName, index) => (
          <Panel
            header={<Text strong>{licenseName}</Text>}
            key={index}
            onClick={() => {
              if (!licenseDetails[licenseName]) {
                fetchLicenseDetails(licenseName); // Fetch details if not already fetched
              }
            }}
          >
            {loadingLicense === licenseName ? (
              <Skeleton active paragraph={{ rows: 4 }} />
            ) : (
              <div>
                <Title level={5}>{licenseName} License Details</Title>
                <Text type="secondary" style={{ whiteSpace: "pre-line" }}>
                  {licenseDetails[licenseName] || "Click to load details..."}
                </Text>
              </div>
            )}
          </Panel>
        ))}
      </Collapse>
    </div>
  );
}

export default Licenses;