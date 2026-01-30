import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const repositoriesApi = createApi({
  reducerPath: "repositoryApi",
  baseQuery: customBaseQuery,
  tagTypes: ["Repositories", "RepositoryDetails"],
  endpoints: (builder) => ({
    fetchRepositories: builder.query({
      query: ({ project_id }) => ({
        url: `/crscan/repository?project_id=${project_id}`,
      }),
      providesTags: ["Repositories"],
    }),
    addRepository: builder.mutation({
      query: (repositoryData) => ({
        url: "/crscan/repository",
        method: "POST",
        body: repositoryData,
      }),
      invalidatesTags: ["Repositories"],
    }),
    fetchRepositoryDetails: builder.query({
      query: (id) => ({ url: `/crscan/repository/${id}` }),
      providesTags: ["RepositoryDetails"],
    }),
    updateRepository: builder.mutation({
      query: ({ id, repositoryData }) => ({
        url: `/crscan/repository/${id}`,
        method: "PUT",
        body: repositoryData,
      }),
      invalidatesTags: ["Repositories", "RepositoryDetails"],
    }),
    deleteRepository: builder.mutation({
      query: (id) => ({
        url: `/crscan/repository/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Repositories"],
    }),
  }),
});

export const {
  useFetchRepositoriesQuery,
  useAddRepositoryMutation,
  useFetchRepositoryDetailsQuery,
  useUpdateRepositoryMutation,
  useDeleteRepositoryMutation,
} = repositoriesApi;
