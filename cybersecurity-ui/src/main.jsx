import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { persistor, store } from "./store/store.js";
import { ConfigProvider, message } from "antd";

const theme = {
  token: {
    colorPrimary: "#113032",
    colorError: "#EC4D4F",
    colorWarning: "#FFF962",
    colorSuccess: "#52c41a",
    colorInfo: "#1890ff",
    // Button-specific colors
    colorPrimaryHover: "#6BE992", // Hover color for primary buttons
    colorPrimaryActive: "#5BC67C", // Active color for primary buttons
    colorPrimaryText: "#ffffff", // Text color for primary buttons
    colorPrimaryTextHover: "#d9d9d9", // Text color when hovered
  },
};

message.config({
  duration: 1,
  maxCount: 0,
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <ConfigProvider theme={theme}>
          <App />
        </ConfigProvider>
      </PersistGate>
    </Provider>
  </StrictMode>
);
