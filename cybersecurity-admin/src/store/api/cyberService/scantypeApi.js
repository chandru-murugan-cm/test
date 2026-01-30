import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const scantypesApi = createApi({
  reducerPath: "scantypeApi", // Ensure this matches your Redux store key
  baseQuery: customBaseQuery,
  tagTypes: ["Scanner", "ScannerDetails"],
  endpoints: (builder) => ({
    fetchScannerTypes: builder.query({
      query: () => ({ url: "/cs/scanner-types" }),
      providesTags: ["ScanType"],
    }),

    addScanner: builder.mutation({
      query: (scannerData) => ({
        url: "/cs/scanner-types",
        method: "POST",
        body: scannerData,
      }),
      invalidatesTags: ["ScanType"],
    }),


    fetchScannerDetails: builder.query({
      query: (id) => ({ url: `/cs/scanner-types/${id}` }), 
      providesTags: ["ScanTypeDetails"],
    }),


    updateScanner: builder.mutation({
      query: ({ id, scannerData }) => ({
        url: `/cs/scanner-types/${id}`,
        method: "PUT",
        body: scannerData,
  
      }),
      invalidatesTags: ["ScanType", "ScanTypeDetails"],
    }),



    deleteScanner: builder.mutation({
      query: ({id}) => ({
        url: `/cs/scanner-types/${id}`, 
        method: "DELETE",
      }),
      invalidatesTags: ["ScanType"],
    }),

    getScanTargets: builder.query({
      query: () => ({ url: "/cs/scanner-types/scan-target-types" }),
      method: "GET",
    }),
  }),
});

export const {
  useFetchScannerTypesQuery,
  useAddScannerMutation,
  useFetchScannerDetailsQuery,
  useUpdateScannerMutation,
  useDeleteScannerMutation,
  useGetScanTargetsQuery,
} = scantypesApi;
