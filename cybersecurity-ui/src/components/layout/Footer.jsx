import React from "react";
import { Layout } from "antd";

const { Footer: AntFooter } = Layout;

const Footer = () => {
  return (
    <AntFooter
      style={{
        textAlign: "center",
        backgroundColor: "#001529",
        color: "white",
        padding: "20px 0",
      }}
    >
      © {new Date().getFullYear()} Cyber Security. All Rights Reserved.
    </AntFooter>
  );
};

export default Footer;
