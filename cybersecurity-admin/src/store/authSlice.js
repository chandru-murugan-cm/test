// src/store/authSlice.js
import { createSlice } from "@reduxjs/toolkit";

const authSlice = createSlice({
  name: "auth",
  initialState: {
    token: null,
    user: null,
    isAuthenticated: false,
    selectedProject: null, // New field to store selected project
  },
  reducers: {
    login(state, action) {
      state.token = action.payload.token;
      state.user = action.payload.user;
      state.isAuthenticated = true;
    },
    logout(state) {
      state.token = null;
      state.user = null;
      state.isAuthenticated = false;
      state.selectedProject = null; // Clear selected project on logout
    },
    setSelectedProject(state, action) {
      state.selectedProject = action.payload; // Action to set the selected project
    },
  },
});

export const { login, logout, setSelectedProject } = authSlice.actions;
export default authSlice.reducer;
