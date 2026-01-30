import React from "react";
import { Breadcrumb } from "antd";
import { useLocation } from "react-router-dom";

const Breadcrumbs = () => {
  const location = useLocation();

  const formatTitle = (title) =>
    title
      .split(/[-/]/)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

  const breadcrumbItems = location.pathname
    .split("/")
    .filter(Boolean)
    .map((item, index, array) => ({
      title: formatTitle(item),
      path: "/" + array.slice(0, index + 1).join("/"),
    }));

  return (
    <Breadcrumb style={{ marginLeft: "16px", fontSize: "16px" }}>
      {breadcrumbItems.map((item, index) => (
        <Breadcrumb.Item key={index}>
          <a href={item.path}>{item.title}</a>
        </Breadcrumb.Item>
      ))}
    </Breadcrumb>
  );
};

export default Breadcrumbs;
