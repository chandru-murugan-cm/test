// src/store/authSlice.js
import { createSlice } from "@reduxjs/toolkit";

const authSlice = createSlice({
  name: "auth",
  initialState: {
    token: null,
    user: null,
    isAuthenticated: false,
    selectedProject: null,
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
      state.selectedProject = null;
    },
    setSelectedProject(state, action) {
      state.selectedProject = action.payload;
    },
    setSammScore(state, action) {
      state.sammScore = action.payload;
    },
  },
});

export const { login, logout, setSelectedProject, setSammScore } =
  authSlice.actions;
export default authSlice.reducer;
