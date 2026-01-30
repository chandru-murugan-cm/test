import { Progress, Typography } from "antd";

const { Text } = Typography;

const ProgressBar = ({ progressPercentage, loading }) => {
  const isComplete = progressPercentage === "100.0";

  // Set progress color dynamically
  const progressColor = isComplete
    ? "linear-gradient(to right, #4caf50, #66bb6a)" // green for completion
    : "linear-gradient(to right, #ff9800, #ff5722)"; // orange for progress

  return (
    <div
      style={{
        marginTop: "20px",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        marginBottom: "20px",
      }}
    >
      {/* Horizontal Progress Bar */}
      <Progress
        percent={progressPercentage}
        status={isComplete ? "success" : "active"}
        strokeColor={{
          "0%": "#ff9800",
          "100%": isComplete ? "#4caf50" : "#ff5722",
        }}
        trailColor="#ddd"
        strokeWidth={24}
        showInfo={true} // hide default percent info
        style={{
          width: "100%",
          maxWidth: "600px",
          overflow: "hidden",
          marginBottom: "10px",
        }}
      />

      {/* Text Status */}
      <Text
        style={{
          fontSize: "18px",
          fontWeight: 500,
          color: isComplete ? "#4caf50" : "#ff9800",
          marginTop: "8px",
        }}
      >
        {!loading ? "Scan completed successfully!" : "Scan is in progress..."}
      </Text>

      {/* Optional: Show percentage below */}
      <Text
        style={{
          fontSize: "16px",
          fontWeight: "bold",
          marginTop: "4px",
          color: isComplete ? "#4caf50" : "#ff9800",
        }}
      >
        {progressPercentage}%
      </Text>
    </div>
  );
};

export default ProgressBar;
