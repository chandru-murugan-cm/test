import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const complianceScannerTypesApi = createApi({
  reducerPath: "complianceScannerTypesApi",
  baseQuery: customBaseQuery,
  tagTypes: ["ComplianceScannerTypes"],
  endpoints: (builder) => ({
    addComplianceScannerTypes: builder.mutation({
      query: (newComplianceScannerTypes) => ({
        url: "/crscan/compliance_scanner_mapping",
        method: "POST",
        body: newComplianceScannerTypes,
      }),
      invalidatesTags: ["ComplianceScannerTypes"],
    }),

    updateComplianceScannerTypes: builder.mutation({
      query: ({ complianceId, updatedData }) => ({
        url: `/crscan/compliance_scanner_mapping/${complianceId}`,
        method: "PUT",
        body: updatedData,
      }),
      invalidatesTags: ["ComplianceScannerTypes"],
    }),
  }),
});

export const {
  useAddComplianceScannerTypesMutation,
  useUpdateComplianceScannerTypesMutation,
} = complianceScannerTypesApi;
