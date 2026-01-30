import axios from "axios";
import { store } from "../store/store";

// Function to create axios instance with dynamic baseURL
const createAxiosInstance = (service) => {
  let baseURL;
  if (service === "auth") {
    baseURL = import.meta.env.VITE_API_AUTH_BASE_URL;
  } else if (service === "cyber-service") {
    baseURL = import.meta.env.VITE_API_CYBER_SERVICE_BASE_URL;
  }

  const axiosInstance = axios.create({
    baseURL: baseURL,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Add token interceptor
  axiosInstance.interceptors.request.use(
    (config) => {
      const token = store.getState().auth.token;
      if (token) {
        config.headers["Authorization"] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  return axiosInstance;
};

export default createAxiosInstance;
