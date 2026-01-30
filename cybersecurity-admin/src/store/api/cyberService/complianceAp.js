import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const complianceApi = createApi({
  reducerPath: "complianceApi",
  baseQuery: customBaseQuery,
  tagTypes: ["Compliances"],
  endpoints: (builder) => ({
    fetchCompliances: builder.query({
      query: (complianceState) => ({
        url: `/crscan/compliance?compliance_type=${complianceState}`,
        method: "GET",
      }),
      providesTags: ["Compliances"],
    }),
    fetchUniqueComplianceTypes: builder.query({
      query: () => ({
        url: "/crscan/compliance/unique/compliance_types",
        method: "GET",
      }),
      providesTags: ["Compliances"],
    }),

    AddCompliance: builder.mutation({
      query: (newCompliance) => ({
        url: "/crscan/compliance",
        method: "POST",
        body: newCompliance,
      }),
      invalidatesTags: ["Compliances"],
    }),

    updateCompliance: builder.mutation({
      query: ({ complianceId, updatedData }) => ({
        url: `/crscan/compliance/${complianceId}`,
        method: "PUT",
        body: updatedData,
      }),
      invalidatesTags: ["Compliances"],
    }),

    deleteCompliance: builder.mutation({
      query: (complianceId) => ({
        url: `/crscan/compliance/${complianceId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Compliances"],
    }),
  }),
});

export const {
  
  useFetchCompliancesQuery,
  useFetchUniqueComplianceTypesQuery,
  useAddComplianceMutation,
  useUpdateComplianceMutation,
  useDeleteComplianceMutation,
} = complianceApi;
