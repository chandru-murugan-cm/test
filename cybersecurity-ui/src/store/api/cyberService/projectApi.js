import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const projectsApi = createApi({
  reducerPath: "projectApi",
  baseQuery: customBaseQuery,
  tagTypes: ["Projects", "ProjectDetails"],
  endpoints: (builder) => ({
    fetchProjects: builder.query({
      query: () => ({ url: "/crscan/project" }),
      providesTags: ["Projects"],
    }),
    addProject: builder.mutation({
      query: (projectData) => ({
        url: "/crscan/project",
        method: "POST",
        body: projectData,
      }),
      invalidatesTags: ["Projects"],
    }),
    fetchProjectDetails: builder.query({
      query: (id) => ({ url: `/crscan/project/${id}` }),
      providesTags: ["ProjectDetails"],
    }),
    updateProject: builder.mutation({
      query: ({ id, projectData }) => ({
        url: `/crscan/project/${id}`,
        method: "PUT",
        body: projectData,
      }),
      invalidatesTags: ["Projects", "ProjectDetails"],
    }),
    deleteProject: builder.mutation({
      query: (id) => ({
        url: `/crscan/project/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Projects"],
    }),
  }),
});

export const {
  useFetchProjectsQuery,
  useAddProjectMutation,
  useFetchProjectDetailsQuery,
  useUpdateProjectMutation,
  useDeleteProjectMutation,
} = projectsApi;
