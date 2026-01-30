import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery"; // Assuming customBaseQuery is defined elsewhere

export const repoScanResultsApi = createApi({
  reducerPath: "repoScanResultsApi",
  baseQuery: customBaseQuery,
  tagTypes: ["RepoScanResults"], // Define the tag type for invalidation
  endpoints: (builder) => ({
    // Endpoint to fetch licenses and SBOM
    fetchLicensesAndSbom: builder.query({
      query: (project_id) => ({
        url: `/crscan/repo_scan/licenses_and_sbom/${project_id}`,
      }),
      providesTags: ["RepoScanResults"], // Tags to invalidate if needed
    }),
    // Endpoint to fetch licenses by project ID
    fetchLicensesByProjectId: builder.query({
      query: (project_id) => ({
        url: `/crscan/repo_scan/licenses/${project_id}`,
      }),
      providesTags: ["RepoScanResults"], 
    }),
    // Endpoint to fetch licenses grouped by type and risk
    fetchLicensesGroupByTypeAndRisk: builder.query({
      query: (project_id) => ({
        url: `/crscan/repo_scan/licenses_and_sbom/group/${project_id}`, // Grouped by type and risk
      }),
      providesTags: ["RepoScanResults"], // Tags to invalidate if needed
    }),
    // Endpoint to fetch sbom vuln by type and risk
    fetchSbomVuln: builder.query({
      query: (project_id) => ({
        url: `/crscan/repo_scan/licenses_and_sbom/vuln/${project_id}`, // Grouped by type and risk
      }),
      providesTags: ["RepoScanResults"], // Tags to invalidate if needed
    }),
    fetchLanguagesAndFrameworkByProjectId: builder.query({
      query: (project_id) => ({
        url: `/crscan/languages_and_framework/${project_id}`,
      }),
      providesTags: ["RepoScanResults"],
    }),
  }),
});

export const {
  useFetchLicensesAndSbomQuery,
  useFetchLicensesByProjectIdQuery,
  useFetchLicensesGroupByTypeAndRiskQuery,
  useFetchLanguagesAndFrameworkByProjectIdQuery,
  useFetchSbomVulnQuery,
} = repoScanResultsApi;
