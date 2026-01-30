import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const asvsApi = createApi({
  reducerPath: "asvsApi",
  baseQuery: customBaseQuery,
  tagTypes: ["Asvs", "OwaspTopTen"],
  endpoints: (builder) => ({
    fetchAsvs: builder.query({
      query: (params) => ({
        url: "/crscan/asvs",
        method: "GET",
        params,
      }),
      providesTags: ["Asvs"],
    }),
    fetchOwaspTopTen: builder.query({
      query: (params) => ({
        url: "/crscan/owasp_top_ten",
        method: "GET",
        params,
      }),
      providesTags: ["OwaspTopTen"],
    }),
    addAsvs: builder.mutation({
      query: (asvsData) => ({
        url: "/crscan/asvs",
        method: "POST",
        body: asvsData,
      }),
      invalidatesTags: ["Asvs"],
    }),
  }),
});

export const {
  useFetchAsvsQuery,
  useFetchOwaspTopTenQuery,
  useAddAsvsMutation,
} = asvsApi;
