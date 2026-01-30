import React from "react";
import { Link } from "react-router-dom";
import { Button } from "antd";

const NotFound = () => {
  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.header}>404</h1>
        <p style={styles.message}>
          Oops! The page you are looking for does not exist.
        </p>
        <p style={styles.subMessage}>
          You might have followed a broken link or typed the address
          incorrectly.
        </p>
        <Link to="/" style={styles.link}>
          <Button type="primary" size="large" style={styles.button}>
            Go Back Home
          </Button>
        </Link>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#f4f7fa",
    margin: 0,
  },
  content: {
    textAlign: "center",
    padding: "0",
    width: "100%",
    fontFamily: "'Roboto', sans-serif",
  },
  header: {
    fontSize: "80px",
    fontWeight: "bold",
    marginBottom: "16px",
    color: "#ff4d4f",
    marginTop: "-120px",
  },
  message: {
    fontSize: "18px",
    color: "#595959",
    marginBottom: "16px",
  },
  subMessage: {
    fontSize: "16px",
    color: "#8c8c8c",
    marginBottom: "24px",
  },
  link: {
    textDecoration: "none",
  },
  button: {
    borderRadius: "8px",
    padding: "12px 24px",
    fontSize: "16px",
    transition: "all 0.3s ease-in-out",
    background: "#6BE992",
    boxShadow: "none",
  },
};

export default NotFound;
