import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const domainApi = createApi({
  reducerPath: "domainApi",
  baseQuery: customBaseQuery,
  tagTypes: ["Domains", "DomainDetails"],
  endpoints: (builder) => ({
    fetchDomains: builder.query({
      query: ({ project_id }) => ({
        url: `/crscan/domain?project_id=${project_id}`,
        method: "GET",
      }),
      providesTags: ["Domains"],
    }),
    fetchDomainDetails: builder.query({
      query: (id) => ({
        url: `/crscan/domain/${id}`,
        method: "GET",
      }),
      providesTags: ["DomainDetails"],
    }),
    addDomain: builder.mutation({
      query: (domainData) => ({
        url: "/crscan/domain",
        method: "POST",
        body: domainData,
      }),
      invalidatesTags: ["Domains"],
    }),
    updateDomain: builder.mutation({
      query: ({ id, domainData }) => ({
        url: `/crscan/domain/${id}`,
        method: "PUT",
        body: domainData,
      }),
      invalidatesTags: ["Domains", "DomainDetails"],
    }),
    deleteDomain: builder.mutation({
      query: (id) => ({
        url: `/crscan/domain/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Domains"],
    }),
  }),
});

export const {
  useFetchDomainsQuery,
  useFetchDomainDetailsQuery,
  useAddDomainMutation,
  useUpdateDomainMutation,
  useDeleteDomainMutation,
} = domainApi;
