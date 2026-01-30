// src/services/scannerApi.js
import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const scannerApi = createApi({
  reducerPath: "scannerApi",
  baseQuery: customBaseQuery,
  endpoints: (builder) => ({
    fetchScanners: builder.query({
      query: () => ({ url: "/cs/scanners" }),method:"GET",
      providesTags: ["Scanner"],
    }),
    addScanners: builder.mutation({
      query: (scannerData) => ({url: "/cs/scanners",
        method: "POST",
        body: scannerData,
      }),invalidatesTags: ["Scanner"],
    }),
    updateScanners: builder.mutation({
      query: ({ id, scannerData }) => ({url: `/cs/scanners/${id}`,
        method: "PUT",
        body: scannerData,
      }),invalidatesTags: ["Scanner"],
    }),
    deleteScanners: builder.mutation({
      query: ({id}) => ({url: `/cs/scanners/${id}`, 
        method: "DELETE",
      }),
      invalidatesTags: ["Scanner"],
    }),
    fetchScansByProject: builder.query({
      query: (projectId) => ({
        url: `/cs/scans/${projectId}`,
      }),
      providesTags: (result, error, projectId) => [
        { type: "Scans", id: projectId },
      ],
    }),
    fetchFindingsByScanId: builder.query({
      query: (scanId) => ({
        url: `/cs/unformatted_scan/unformatted_result?unformatted_scan_id=${scanId}`,
      }),
    }),
    fetchFindingsByProjectId: builder.query({
      query: ({ projectId, page = 1, limit = 10, targetType, severity, status, orderBy, orderDirection }) => {
        const queryParams = new URLSearchParams({ page, limit });
        if (targetType) {
          queryParams.append("targetType", targetType);
        }
        if (severity) {
          queryParams.append("severity", severity);
        }
        if (status) {
          queryParams.append("status", status);
        }
        if (orderBy) {
          queryParams.append("orderBy", orderBy);
        }
        if (orderDirection) {
          queryParams.append("orderDirection", orderDirection);
        }

        return {
          url: `/cs/finding_master/${projectId}?${queryParams.toString()}`,
        };
      },
      providesTags: (result, error, { projectId }) => [
        { type: "Findings", id: projectId },
      ],
    }),
    fetchDashboardDetails: builder.query({
      query: (projectId) => ({
        url: `/cs/finding_master/counts/${projectId}`,
      }),
    }),
    updateFindingStatus: builder.mutation({
      query: ({ findingId, status }) => ({
        url: `/cs/finding_master/${findingId}/status`,
        method: "PATCH",
        body: { status },
      }),
      invalidatesTags: (result, error, { findingId }) => [
        { type: "Findings", id: findingId }, // Invalidates the specific finding
        // You also need to invalidate the corresponding projectId's findings to trigger refetch
        { type: "Findings", id: result?.projectId }, // Assuming the result contains projectId, else you'll need to pass it
      ],
    }),
    fetchExtendedFindingDetails: builder.query({
      query: (findingId) => ({
        url: `/cs/finding_master/${findingId}/extended_details`,
      }),
    }),
    fetchFixRecommendation: builder.query({
      query: (fix_recommendation_id) => ({
        url: `/cs/finding_master/fix/${fix_recommendation_id}`,
      }),
    }),
  }),
});

export const {
  useFetchScannersQuery,
  useAddScannersMutation,
  useUpdateScannersMutation,
  useDeleteScannersMutation,
  useFetchScansByProjectQuery,
  useFetchFindingsByScanIdQuery,
  useFetchFindingsByProjectIdQuery,
  useFetchDashboardDetailsQuery,
  useUpdateFindingStatusMutation,
  useFetchExtendedFindingDetailsQuery,
  useFetchFixRecommendationQuery
} = scannerApi;
