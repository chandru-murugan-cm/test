import React from "react";
import { Select } from "antd";

const ProjectSelector = ({
  projects,
  selectedProject,
  onChange,
  fetchFindings,
}) => {
  return (
    <Select
      placeholder="Select Project"
      style={{ width: 200, marginRight: 16 }}
      onChange={(value) => {
        onChange(value);
        fetchFindings(value);
      }}
      value={selectedProject}
    >
      {projects.map((project) => (
        <Select.Option key={project.key} value={project.key}>
          {project.projectName}
        </Select.Option>
      ))}
    </Select>
  );
};

export default ProjectSelector;
