import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const asvsApi = createApi({
  reducerPath: "asvsApi",
  baseQuery: customBaseQuery,
  tagTypes: ["ASVS"], 
  endpoints: (builder) => ({
    fetchAsvs: builder.query({
      query: () => ({ url: "/crscan/asvs", method: "GET" }),
      providesTags: ["ASVS"],
    }),
    addAsvs: builder.mutation({
      query: (asvsData) => ({
        url: "/crscan/asvs", 
        method: "POST",
        body: asvsData,  
    }),
      invalidatesTags: [{ type: "ASVS"}],
    }),
    updateAsvs: builder.mutation({
      query: ({ id, asvsData }) => ({url: `/crscan/asvs/${id}`,
        method: "PUT",
        body: asvsData,
      }),
      invalidatesTags: [{ type: "ASVS"}],
    }),
    deleteAsvs: builder.mutation({
      query: ({ id }) => ({
        url: `/crscan/asvs/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "ASVS"}],
    }),
  }),
});

export const {
  useFetchAsvsQuery,
  useAddAsvsMutation,
  useUpdateAsvsMutation,
  useDeleteAsvsMutation,
} = asvsApi;
