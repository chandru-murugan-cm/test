import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const complianceApi = createApi({
  reducerPath: "complianceApi",
  baseQuery: customBaseQuery,
  tagTypes: ["Compliances"],
  endpoints: (builder) => ({
    fetchCompliances: builder.query({
      query: ({ complianceState, project_id }) => ({
        url: `/crscan/compliance?compliance_type=${complianceState}&project_id=${project_id}`,
        method: "GET",
      }),
      providesTags: ["Compliances"],
    }),

    fetchComplianceSummary: builder.query({
      query: (project_id) => ({
        url: `/crscan/compliance/summary?project_id=${project_id}`,
        method: "GET",
      }),
      providesTags: ["Compliances"],
    }),

    createManualComplianceEvaluation: builder.mutation({
      query: (complianceData) => ({
        url: "/crscan/manual_compliance_evaluation",
        method: "POST",
        body: complianceData,
      }),
      invalidatesTags: ["Compliances"],
    }),
  }),
});

export const {
  useFetchCompliancesQuery,
  useFetchComplianceSummaryQuery,
  useCreateManualComplianceEvaluationMutation,
} = complianceApi;
