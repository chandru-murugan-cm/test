import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const sammApi = createApi({
  reducerPath: "sammApi",
  baseQuery: customBaseQuery,
  tagTypes: ["Samm"],
  endpoints: (builder) => ({
    fetchSamm: builder.query({
      query: (params) => ({
        url: "/crscan/samm",
        method: "GET",
        params,
      }),
      providesTags: ["Frameworks"],
    }),
    addSamm: builder.mutation({
      query: (sammData) => ({
        url: "/crscan/samm",
        method: "POST",
        body: sammData,
      }),
      invalidatesTags: ["Samm"],
    }),
    updateSamm: builder.mutation({
      query: ({ sammId, updatedData }) => ({
        url: `/crscan/samm/${sammId}`,
        method: "PUT",
        body: updatedData,
      }),
      invalidatesTags: ["Samm"],
    }),
    deleteSamm: builder.mutation({
      query: (sammId) => ({
        url: `/crscan/samm/${sammId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Samm"],
    }),
    fetchBusinessfunctions: builder.query({
      query: () => ({
        url: "/crscan/samm/l1_business_function",
        method: "GET",
      }),
      providesTags: ["Businessfunctions"], 
    }),
  }),
});

export const { 
  useFetchSammQuery,
  useAddSammMutation,
  useUpdateSammMutation,
  useDeleteSammMutation,
  useFetchBusinessfunctionsQuery, 
} = sammApi;

