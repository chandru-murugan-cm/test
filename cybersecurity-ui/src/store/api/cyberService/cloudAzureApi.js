import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const cloudAzureApi = createApi({
  reducerPath: "cloudAzureApi",
  baseQuery: customBaseQuery,
  tagTypes: ["CloudAzure", "CloudAzureDetails"],
  endpoints: (builder) => ({
    // Fetch all TargetAzureCloud records
    fetchCloudAzure: builder.query({
      query: () => ({ url: "/crscan/cloud/azure" }),
      providesTags: ["CloudAzure"],
    }),

    // Add a new TargetAzureCloud record
    addCloudAzure: builder.mutation({
      query: (cloudazureData) => ({
        url: "/crscan/cloud/azure",
        method: "POST",
        body: cloudazureData,
      }),
      invalidatesTags: ["CloudAzure"],
    }),

    // Fetch a single TargetAzureCloud record by scans_id (renamed from id)
    fetchCloudAzureDetails: builder.query({
      query: (scans_id) => ({ url: `/crscan/cloud/azure?scans_id=${scans_id}` }),
      providesTags: ["CloudAzureDetails"],
    }),

    // Delete an TargetAzureCloud record by azure_id
    deleteCloudAzure: builder.mutation({
      query: (azure_id) => ({
        url: `/crscan/cloud/azure/${azure_id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["CloudAzure"],
    }),

    // Fetch TargetAzureCloud records by project_id
    fetchCloudAzureByProjectId: builder.query({
      query: (project_id) => ({ url: `/crscan/cloud/azure/${project_id}` }),
      providesTags: ["CloudAzure"],
    }),

    // Fetch TargetAzureCloud records by name
    fetchCloudAzureByName: builder.query({
      query: (name) => ({ url: `/crscan/cloud/azure/name/${name}` }),
      providesTags: ["CloudAzure"],
    }),

  }),
});

export const {
  useFetchCloudAzureQuery,
  useAddCloudAzureMutation,
  useFetchCloudAzureDetailsQuery,
  useDeleteCloudAzureMutation,
  useFetchCloudAzureByProjectIdQuery,
  useFetchCloudAzureByNameQuery,
} = cloudAzureApi;
