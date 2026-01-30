import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const owasptoptenScannerTypeApi = createApi({
  reducerPath: "owasptoptenScannerTypeApi",
  baseQuery: customBaseQuery,
  tagTypes: ["OwasptoptenScannerTypes"],
  endpoints: (builder) => ({
    addOwasptoptenScannerTypes: builder.mutation({
      query: (newOwasptoptenScannerTypes) => ({
        url: "/crscan/owasptopten_scanner_mapping",
        method: "POST",
        body: newOwasptoptenScannerTypes,
      }),
      invalidatesTags: ["OwasptoptenScannerTypes"],
    }),

    updateOwasptoptenScannerTypes: builder.mutation({
      query: ({ owasp_top_ten_id, updatedData }) => ({
        url: `/crscan/owasptopten_scanner_mapping/${owasp_top_ten_id}`,  
        method: "PUT",
        body: updatedData,
      }),
      invalidatesTags: ["OwasptoptenScannerTypes"],
    }),
    
    fetchOwasptoptenScannerType: builder.query({
      query: (params) => {
        let queryString = "";
        if (params) {
          queryString = "?" + new URLSearchParams(params).toString();
        }
        return {
          url: `/crscan/owasptopten_with_scanner_types${queryString}`,
          method: "GET",
        };
      },
      providesTags: ["OwasptoptenScannerTypes"],
    }),
  }),
});

export const {
  useAddOwasptoptenScannerTypesMutation,
  useUpdateOwasptoptenScannerTypesMutation,
  useFetchOwasptoptenScannerTypeQuery,
} = owasptoptenScannerTypeApi;
