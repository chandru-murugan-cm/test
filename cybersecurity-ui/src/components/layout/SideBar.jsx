import React, { useEffect, useState } from "react";
import {
  Layout,
  Menu,
  Button,
  Dropdown,
  Space,
  Modal,
  Input,
  message,
  Form,
} from "antd";
import {
  DashboardOutlined,
  AppstoreOutlined,
  FileSearchOutlined,
  SecurityScanOutlined,
  WarningOutlined,
  LogoutOutlined,
  PlusOutlined,
  ContainerOutlined,
  DatabaseOutlined,
  GlobalOutlined,
  ClusterOutlined,
  CheckCircleOutlined,
  SettingOutlined,
  DownOutlined,
  Html5Filled,
  NotificationOutlined,
  CloudOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  DeploymentUnitOutlined,
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import {
  useFetchProjectsQuery,
  useAddProjectMutation,
} from "../../store/api/cyberService/projectApi";
import { setSelectedProject } from "../../store/authSlice";
import Logo from "../../assets/images/logo.png";

const { Sider } = Layout;
const { SubMenu } = Menu;
const { TextArea } = Input;

const Sidebar = ({ collapsed, toggleCollapse, handleLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();

  // State for modal visibility
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [projectDetails, setProjectDetails] = useState("");
  const user = useSelector((state) => state.auth.user);

  // Fetch the projects
  const { data, isLoading, refetch } = useFetchProjectsQuery();
  const [addProject, { isLoading: isAdding }] = useAddProjectMutation();
  const projects = data?.data || [];

  // Get the selected project from Redux
  const selectedProject = useSelector((state) => state.auth.selectedProject);
  const projectExists = projects.some((p) => p?._id === selectedProject?._id);

  useEffect(() => {
    if (
      (projects && !selectedProject) ||
      (projects?.length > 0 && selectedProject && !projectExists)
    ) {
      dispatch(setSelectedProject(projects[0]));
    }
  }, [projects, selectedProject, dispatch, user?.userId]);

  useEffect(() => {
    const fetchProjectsAndDispatch = async () => {
      try {
        const { data } = await refetch();
        if (data && data.data.length > 0 && !selectedProject) {
          dispatch(setSelectedProject(data.data[0]));
        }
      } catch (error) {
        console.error("Failed to fetch projects:", error);
      }
    };

    fetchProjectsAndDispatch();
  }, [user?.userId, dispatch, refetch]);

  // Handle project selection
  const handleProjectSelect = (projectId) => {
    const project = projects.find((p) => p._id === projectId);
    dispatch(setSelectedProject(project));
    localStorage.setItem("selectedProject", JSON.stringify(project));
  };

  // Handle "Add New Project" button click
  const handleAddProjectClick = () => {
    setIsModalVisible(true);
  };

  // Handle modal submission
  const handleAddProjectSubmit = async () => {
    if (!newProjectName.trim()) {
      message.error("Project name is required");
      return;
    }
    try {
      await addProject({
        name: newProjectName,
        description: projectDetails,
        domain_value: "",
        repo_url: "",
        organization: "",
      }).unwrap();
      message.success("Project added successfully");
      setIsModalVisible(false);
      setNewProjectName("");
    } catch (error) {
      message.error("Failed to add project. Please try again.");
    }
  };

  // Dropdown menu for projects
  const projectMenu = (
    <Menu
      style={{
        borderRadius: "8px",
        padding: "10px 0",
        boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
        minWidth: "200px",
        maxHeight: "600px",
        overflowY: "scroll",
        overflowX: "hidden",
      }}
    >
      {projects?.map((project) => (
        <Menu.Item
          key={project._id}
          onClick={() => handleProjectSelect(project._id)}
          style={{
            padding: "8px 20px",
            fontSize: "14px",
            display: "flex",
            alignItems: "center",
            borderRadius: "6px",
            transition: "background-color 0.3s ease",
          }}
        >
          <AppstoreOutlined style={{ marginRight: "10px" }} />
          {project.name}
        </Menu.Item>
      ))}
      <Menu.Divider />
      <Menu.Item
        key="add-project"
        onClick={handleAddProjectClick}
        style={{
          padding: "8px 20px",
          fontSize: "14px",
          display: "flex",
          alignItems: "center",
          borderRadius: "6px",
          transition: "background-color 0.3s ease",
        }}
      >
        <PlusOutlined style={{ marginRight: "10px" }} />
        Add New Project
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      <Sider
        collapsible
        collapsed={collapsed}
        width={250}
        trigger={null}
        style={{
          background: "#113032",
          position: "fixed",
          height: "100vh",
          left: 0,
          overflow: "auto",
          boxShadow: "2px 0 5px rgba(0, 0, 0, 0.1)",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "20px",
            paddingBottom: "5px",
            fontSize: "20px",
            fontWeight: "bold",
            color: "#fff",
            textAlign: "center",
            background: "#113032",
          }}
        >
          {collapsed ? "DCW" : <img src={Logo} alt="DCC CyberWacht Logo" />}
        </div>

        {/* Project Selector */}
        <div
          style={{
            padding: "10px 16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Dropdown
            overlay={projectMenu}
            trigger={["click"]}
            style={{ flex: 1 }}
          >
            <div
              style={{
                background: "#113032",
                borderRadius: "8px",
                padding: "6px 10px",
                color: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                fontWeight: "500",
                border: "0.5px solid #6BE992",
                fontSize: 13,
                width: "90%",
              }}
            >
              <span>
                {collapsed
                  ? ""
                  : selectedProject && selectedProject.name
                  ? selectedProject.name
                  : "Select Project"}
              </span>
              <DownOutlined style={{ color: "white", fontSize: "14px" }} />
            </div>
          </Dropdown>
          <SettingOutlined
            style={{
              fontSize: "30px",
              marginLeft: "16px", // Adjusting space between dropdown and setting icon
              cursor: "pointer",
              color: "#6BE992",
            }}
            onClick={() => navigate(`/project`)}
          />
        </div>

        {/* Sidebar Menu */}
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={["/"]}
          selectedKeys={[location.pathname]}
          style={{
            height: "calc(100% - 150px)",
            borderRight: 0,
            backgroundColor: "#113032",
          }}
          defaultOpenKeys={["findings"]}
        >
          <Menu.Item
            key="/"
            icon={<DashboardOutlined />}
            onClick={() => navigate("/")}
            style={{
              marginBottom: "-4px",
              color: location.pathname === "/" ? "#6BE992" : "inherit",
            }}
          >
            Dashboard
          </Menu.Item>
          <Menu.Item
            key="/compliance"
            icon={<SettingOutlined />}
            onClick={() => navigate("/compliance")}
            style={{
              marginBottom: "-4px",
              color:
                location.pathname === "/compliance" ? "#6BE992" : "inherit",
            }}
          >
            Compliance
          </Menu.Item>
          <Menu.Item
            key="/compliance"
            icon={<BranchesOutlined />}
            onClick={() => navigate("/frameworks")}
            style={{
              marginBottom: "-4px",
              color: location.pathname.startsWith("/frameworks")
                ? "#6BE992"
                : "inherit",
            }}
          >
            Frameworks
          </Menu.Item>
          <Menu.Divider
            style={{
              borderBottomColor: "#3D856B",
              borderBottomWidth: "0.1px",
              margin: "18px 15px",
            }}
          />
          <Menu.Item
            key="/scans"
            icon={<SecurityScanOutlined />}
            onClick={() => navigate("/scans")}
            style={{
              marginBottom: "-4px",
              color: location.pathname === "/scans" ? "#6BE992" : "inherit",
            }}
          >
            Scans
          </Menu.Item>
          <SubMenu
            key="findings"
            icon={
              <WarningOutlined
                style={{
                  color: location.pathname.startsWith("/findings")
                    ? "#6BE992"
                    : "inherit",
                }}
              />
            }
            title={
              <span
                style={{
                  color: location.pathname.startsWith("/findings")
                    ? "#6BE992"
                    : "inherit",
                }}
              >
                Findings
              </span>
            }
            onTitleClick={() => navigate("/findings")}
            style={{
              marginBottom: "-4px",
            }}
            className="findings-submenu"
          >
            <Menu.Item
              key="/repositories"
              icon={<DatabaseOutlined />}
              onClick={() => navigate("/repositories")}
              style={{
                marginBottom: "-4px",
                color:
                  location.pathname === "/repositories" ? "#6BE992" : "inherit",
              }}
            >
              Repositories
            </Menu.Item>
            <Menu.Item
              key="/domains"
              icon={<GlobalOutlined />}
              onClick={() => navigate("/domains")}
              style={{
                marginBottom: "-4px",
                color: location.pathname === "/domains" ? "#6BE992" : "inherit",
              }}
            >
              Domains
            </Menu.Item>
            <Menu.Item
              key="/contracts"
              icon={<ClusterOutlined />}
              onClick={() => navigate("/contracts")}
              style={{
                marginBottom: "-4px",
                color:
                  location.pathname === "/contracts" ? "#6BE992" : "inherit",
              }}
            >
              Web3
            </Menu.Item>
            <Menu.Item
              key="/cloud"
              icon={<CloudOutlined />}
              onClick={() => navigate("/cloud")}
              style={{
                marginBottom: "-4px",
                color: location.pathname === "/cloud" ? "#6BE992" : "inherit",
              }}
            >
              Clouds
            </Menu.Item>
            <Menu.Item
              key="/containers"
              icon={<ContainerOutlined />}
              // onClick={() => navigate("/containers")}
              style={{
                marginBottom: "-4px",
              }}
            >
              Containers
            </Menu.Item>
            <Menu.Item
              key="/vms"
              icon={<NodeIndexOutlined />}
              // onClick={() => navigate("/vms")}
              style={{
                marginBottom: "-4px",
              }}
            >
              VMs
            </Menu.Item>
          </SubMenu>

          <Menu.Divider
            style={{
              borderBottomColor: "#3D856B",
              borderWidth: "0.3px",
              margin: "18px 15px",
            }}
          />

          <Menu.Item
            key="/license"
            icon={<CheckCircleOutlined />}
            onClick={() => navigate("/license")}
            style={{
              marginBottom: "-4px",
              color: location.pathname === "/license" ? "#6BE992" : "inherit",
            }}
          >
            License & SBOM
          </Menu.Item>
          <Menu.Item
            key="/framework"
            icon={<Html5Filled />}
            onClick={() => navigate("/languages")}
            style={{
              marginBottom: "-4px",
              color: location.pathname === "/languages" ? "#6BE992" : "inherit",
            }}
          >
            Languages
          </Menu.Item>

          <Menu.Divider
            style={{
              borderBottomColor: "#3D856B",
              borderWidth: "0.3px",
              margin: "18px 15px",
            }}
          />

          <Menu.Item
            key="/vapt-reports"
            icon={<DeploymentUnitOutlined />}
            onClick={() => navigate("/vapt-reports")}
            style={{
              marginBottom: "-4px",
              color: location.pathname === "/vapt-reports" ? "#6BE992" : "inherit",
            }}
          >
            VAPT Reports
          </Menu.Item>
          <Menu.Item
            key="/compliance"
            icon={<NotificationOutlined />}
            // onClick={() => navigate("/compliance")}
            style={{
              marginBottom: "-4px",
              color: "inherit",
            }}
          >
            Audit Reports
          </Menu.Item>
        </Menu>
      </Sider>
      {/* Add Project Modal */}
      <Modal
        title="Add New Project"
        visible={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={handleAddProjectSubmit}
        okText={isAdding ? "Adding..." : "Submit"}
        confirmLoading={isAdding}
      >
        <Form layout="vertical">
          {/* Project Name */}
          <Form.Item
            label="Project Name"
            required
            style={{ marginBottom: "15px" }}
          >
            <Input
              placeholder="Enter project name"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
            />
          </Form.Item>

          {/* Project Details */}
          <Form.Item
            label="Project Description"
            required
            style={{ marginBottom: "15px" }}
          >
            <TextArea
              placeholder="Enter project description"
              value={projectDetails}
              onChange={(e) => setProjectDetails(e.target.value)}
              rows={4} // Adjust the rows for better UX
            />
          </Form.Item>
        </Form>
      </Modal>
      ;
    </>
  );
};

export default Sidebar;
