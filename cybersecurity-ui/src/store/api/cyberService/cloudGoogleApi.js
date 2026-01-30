import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const cloudGoogleApi = createApi({
  reducerPath: "cloudGoogleApi",
  baseQuery: customBaseQuery,
  tagTypes: ["CloudGoogle", "CloudGoogleDetails"],
  endpoints: (builder) => ({
    // Fetch all TargetGoogleCloud records
    fetchCloudGoogle: builder.query({
      query: () => ({ url: "/crscan/cloud/google" }),
      providesTags: ["CloudGoogle"],
    }),

    // Add a new TargetGoogleCloud record
    addCloudGoogle: builder.mutation({
      query: (cloudGoogleData) => ({
        url: "/crscan/cloud/google",
        method: "POST",
        body: cloudGoogleData,
      }),
      invalidatesTags: ["CloudGoogle"],
    }),

    // Fetch a single TargetGoogleCloud record by scans_id (renamed from id)
    fetchCloudGoogleDetails: builder.query({
      query: (scans_id) => ({ url: `/crscan/cloud/google?scans_id=${scans_id}` }),
      providesTags: ["CloudGoogleDetails"],
    }),

    // Delete a TargetGoogleCloud record by google_id
    deleteCloudGoogle: builder.mutation({
      query: (google_id) => ({
        url: `/crscan/cloud/google/${google_id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["CloudGoogle"],
    }),

    // Fetch TargetGoogleCloud records by project_id
    fetchCloudGoogleByProjectId: builder.query({
      query: (project_id) => ({ url: `/crscan/cloud/google/${project_id}` }),
      providesTags: ["CloudGoogle"],
    }),

    // Fetch TargetGoogleCloud records by name
    fetchCloudGoogleByName: builder.query({
      query: (name) => ({ url: `/crscan/cloud/google/name/${name}` }),
      providesTags: ["CloudGoogle"],
    }),

  }),
});

export const {
  useFetchCloudGoogleQuery,
  useAddCloudGoogleMutation,
  useFetchCloudGoogleDetailsQuery,
  useDeleteCloudGoogleMutation,
  useFetchCloudGoogleByProjectIdQuery,
  useFetchCloudGoogleByNameQuery,
} = cloudGoogleApi;
