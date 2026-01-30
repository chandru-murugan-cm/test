// src/services/scannerApi.js
import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const scannerApi = createApi({
  reducerPath: "scannerApi",
  baseQuery: customBaseQuery,
  endpoints: (builder) => ({
    fetchScanners: builder.query({
      query: () => ({ url: "/cs/scanners" }),
    }),
    fetchScannerTypes: builder.query({
      query: () => ({ url: "/cs/scanner-types" }),
    }),
    fetchScansByProject: builder.query({
      query: (projectId) => ({
        url: `/cs/scans/${projectId}`,
      }),
      providesTags: (result, error, projectId) => [
        { type: "Scans", id: projectId }, // Ensure it uses the correct tag type and projectId
      ],
    }),
    fetchFindingsByScanId: builder.query({
      query: (scanId) => ({
        url: `/cs/unformatted_scan/unformatted_result?unformatted_scan_id=${scanId}`,
      }),
    }),
    fetchFindingsByProjectId: builder.query({
      query: ({
        projectId,
        page = 1,
        limit = 10,
        targetType,
        severity,
        status,
        orderBy,
        orderDirection,
        scanTypeIds = [],
      }) => {
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
        if (scanTypeIds.length > 0) {
          queryParams.append("scanTypeIds", scanTypeIds?.join(","));
        }

        return {
          url: `/crscan/finding_master/${projectId}?${queryParams.toString()}`,
        };
      },
      providesTags: (result, error, { projectId }) => [
        { type: "Findings", id: projectId },
      ],
    }),
    fetchDashboardDetails: builder.query({
      query: (projectId) => ({
        url: `/crscan/finding_master/counts/${projectId}`,
      }),
    }),
    updateFindingStatus: builder.mutation({
      query: ({ findingId, status }) => ({
        url: `/crscan/finding_master/${findingId}/status`,
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
        url: `/crscan/finding_master/${findingId}/extended_details`,
      }),
    }),
    fetchFixRecommendation: builder.query({
      query: (fix_recommendation_id) => ({
        url: `/crscan/finding_master/fix/${fix_recommendation_id}`,
      }),
    }),
    checkFindingsBulk: builder.query({
      query: (targetIds) => ({
        url: `/crscan/finding_master/has_findings_bulk`,
        method: "POST",
        body: { target_ids: targetIds },
      }),
    }),
  }),
});

export const {
  useFetchScannersQuery,
  useFetchScannerTypesQuery,
  useFetchScansByProjectQuery,
  useFetchFindingsByScanIdQuery,
  useFetchFindingsByProjectIdQuery,
  useFetchDashboardDetailsQuery,
  useUpdateFindingStatusMutation,
  useFetchExtendedFindingDetailsQuery,
  useFetchFixRecommendationQuery,
  useCheckFindingsBulkQuery,
} = scannerApi;
