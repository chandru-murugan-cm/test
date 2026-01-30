import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const sammApi = createApi({
  reducerPath: "sammApi",
  baseQuery: customBaseQuery,
  tagTypes: ["Samm"],
  endpoints: (builder) => ({
    fetchSamm: builder.query({
      query: ({ projectId }) => ({
        url: `/crscan/samm?project_id=${projectId}`,
        method: "GET",
      }),
      providesTags: ["Samm"],
    }),
    addSamm: builder.mutation({
      query: (sammData) => ({
        url: "/crscan/samm",
        method: "POST",
        body: sammData,
      }),
      invalidatesTags: ["Samm"],
    }),
  }),
});

export const { useFetchSammQuery, useAddSammMutation } = sammApi;
