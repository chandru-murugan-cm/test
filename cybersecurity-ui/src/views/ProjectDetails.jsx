import React, { useEffect } from "react";
import { Spin, message } from "antd";
import { useFetchProjectDetailsQuery } from "../store/api/cyberService/projectApi";
import AccountSettings from "../components/projects/AccountSettings";
import { useSelector } from "react-redux";

const ProjectDetails = () => {
  const selectedProject = useSelector((state) => state.auth.selectedProject);

  // Use the RTK Query hooks for fetching project details and schedules
  const {
    data: projectDetails,
    error: projectError,
    isLoading: projectLoading,
    refetch,
  } = useFetchProjectDetailsQuery(selectedProject?._id, {
    skip: !selectedProject?._id,
  });

  useEffect(() => {
    if (selectedProject?._id) {
      refetch();
    }
  }, [selectedProject?._id, refetch]);

  // Handle loading and error states
  if (projectLoading) {
    return <Spin tip="Loading project details..." />;
  }

  if (projectError) {
    message.error("Error fetching project details.");
  }

  if (!projectDetails) {
    return <div>No project details available.</div>;
  }

  return (
    <div style={{ padding: " 0 24px" }}>
      <AccountSettings
        projectDetails={projectDetails?.data?.[0]}
        refetch={refetch}
      />
    </div>
  );
};

export default ProjectDetails;
