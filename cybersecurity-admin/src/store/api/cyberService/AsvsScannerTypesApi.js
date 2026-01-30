import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const asvsScannerTypeApi = createApi({
  reducerPath: "asvsScannerTypeApi",
  baseQuery: customBaseQuery,
  tagTypes: ["AsvsScannerTypes"],
  endpoints: (builder) => ({
    addAsvsScannerTypes: builder.mutation({
      query: (newAsvsScannerTypes) => ({
        url: "/crscan/asvs_scanner_mapping",
        method: "POST",
        body: newAsvsScannerTypes,
      }),
      invalidatesTags: ["AsvsScannerTypes"],
    }),

    updateAsvsScannerTypes: builder.mutation({
      query: ({ asvs_id, updatedData }) => ({
        url: `/crscan/asvs_scanner_mapping/${asvs_id}`,  
        method: "PUT",
        body: updatedData,
      }),
      invalidatesTags: ["AsvsScannerTypes"],
    }),
    
    fetchAsvsScannerType: builder.query({
      query: (params) => {
        let queryString = "";
        if (params) {
          queryString = "?" + new URLSearchParams(params).toString();
        }
        return {
          url: `/crscan/asvs_with_scanner_types${queryString}`,
          method: "GET",
        };
      },
      providesTags: ["AsvsScannerTypes"],
    }),
  }),
});

export const {
  useAddAsvsScannerTypesMutation,
  useUpdateAsvsScannerTypesMutation,
  useFetchAsvsScannerTypeQuery,
} = asvsScannerTypeApi;
