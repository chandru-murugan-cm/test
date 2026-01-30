import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const frameworkScannerTypesApi = createApi({
  reducerPath: "frameworkScannerTypesApi",
  baseQuery: customBaseQuery,
  tagTypes: ["FrameworkScannerTypes"],
  endpoints: (builder) => ({
    addFrameworkScannerType: builder.mutation({
      query: (newFrameworkScannerType) => ({
        url: "/crscan/framework_scanner_mapping",
        method: "POST",
        body: newFrameworkScannerType,
      }),
      invalidatesTags: ["FrameworkScannerTypes"],
    }),

    updateFrameworkScannerType: builder.mutation({
      query: ({ frameworkId, updatedData }) => ({
        url: `/crscan/framework_scanner_mapping/${frameworkId}`,
        method: "PUT",
        body: updatedData,
      }),
      invalidatesTags: ["FrameworkScannerTypes"],
    }),

    fetchFrameworkScannerType: builder.query({
      query: (params) => {
        let queryString = "";
        if (params) {
          queryString = "?" + new URLSearchParams(params).toString();
        }
        return {
          url: `/crscan/framework_with_scanner_types${queryString}`,
          method: "GET",
        };
      },
      providesTags: ["FrameworkScannerTypes"],
    }),
  }),
});

export const {
  useAddFrameworkScannerTypeMutation,
  useUpdateFrameworkScannerTypeMutation,
  useFetchFrameworkScannerTypeQuery,                    
} = frameworkScannerTypesApi;
