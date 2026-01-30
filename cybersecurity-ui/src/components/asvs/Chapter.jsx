import React from "react";
import { Collapse, Typography, List } from "antd";
import { useFetchAsvsQuery } from "../../store/api/cyberService/asvsApi";

const { Panel } = Collapse;
const { Text } = Typography;

function Chapter() {
  const { data, isLoading, error } = useFetchAsvsQuery();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error fetching data</div>;

  // Group data by chapter_id and chapter_name
  const groupedData = data.data.reduce((acc, item) => {
    const { chapter_id, chapter_name, section_id, section_name } = item;

    // Find or create the chapter group
    if (!acc[chapter_id]) {
      acc[chapter_id] = {
        chapter_id,
        chapter_name,
        sections: {},
      };
    }

    // Find or create the section group within the chapter
    if (!acc[chapter_id].sections[section_id]) {
      acc[chapter_id].sections[section_id] = {
        section_id,
        section_name,
        requirements: [],
      };
    }

    // Add the requirement to the section
    acc[chapter_id].sections[section_id].requirements.push(item);

    return acc;
  }, {});

  // Convert the grouped data object to an array and sort chapters
  const chapters = Object.values(groupedData).sort((a, b) => {
    const aNum = parseInt(a.chapter_id.replace("V", ""), 10);
    const bNum = parseInt(b.chapter_id.replace("V", ""), 10);
    return aNum - bNum;
  });

  return (
    <div style={{ margin: "0 auto" }}>
      <Collapse accordion bordered={false}>
        {chapters.map((chapter) => (
          <Panel
            key={chapter.chapter_id}
            header={
              <Text style={{ fontSize: "16px" }}>
                {chapter.chapter_id} - {chapter.chapter_name}
              </Text>
            }
            style={{
              borderRadius: "4px",
              marginBottom: "8px",
              border: "1px solid #e0e0e0",
              backgroundColor: "#ffffff",
            }}
          >
            <Collapse bordered={false} style={{ backgroundColor: "#ffffff" }}>
              {Object.values(chapter.sections)
                .sort((a, b) => {
                  const aParts = a.section_id.split(".");
                  const bParts = b.section_id.split(".");
                  const aMain = parseInt(aParts[0].replace("V", ""), 10);
                  const bMain = parseInt(bParts[0].replace("V", ""), 10);
                  if (aMain !== bMain) return aMain - bMain;

                  const aSub = parseInt(aParts[1], 10);
                  const bSub = parseInt(bParts[1], 10);
                  return aSub - bSub;
                })
                .map((section) => (
                  <Panel
                    key={section.section_id}
                    header={
                      <Text style={{ fontSize: "14px" }}>
                        {section.section_id} - {section.section_name}
                      </Text>
                    }
                    style={{
                      borderRadius: "4px",
                      marginBottom: "8px",
                      border: "1px solid #d9d9d9",
                    }}
                  >
                    <List
                      size="small"
                      bordered
                      dataSource={section.requirements}
                      renderItem={(req) => (
                        <List.Item>
                          <div>
                            <Text>{req.requirement_name}</Text>
                          </div>
                        </List.Item>
                      )}
                    />
                  </Panel>
                ))}
            </Collapse>
          </Panel>
        ))}
      </Collapse>
    </div>
  );
}

export default Chapter;
