import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const contractApi = createApi({
  reducerPath: "contractApi",
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_CYBER_SERVICE_BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = getState().auth.token;
      if (token) {
        headers.set("authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ["Contracts", "ContractDetails"],
  endpoints: (builder) => ({
    fetchContracts: builder.query({
      query: (params) => ({
        url: "/crscan/contract",
        method: "GET",
        params,
      }),
      providesTags: ["Contracts"],
    }),
    fetchContractDetails: builder.query({
      query: (id) => ({
        url: `/crscan/contract/${id}`,
        method: "GET",
      }),
      providesTags: ["ContractDetails"],
    }),
    addContract: builder.mutation({
      query: (contractData) => ({
        url: "/crscan/contract",
        method: "POST",
        body: contractData,
        // headers: {
        //   "content-type": "multipart/form-data",
        // },
      }),
      invalidatesTags: ["Contracts"],
    }),
    updateContract: builder.mutation({
      query: ({ id, contractData }) => ({
        url: `/crscan/contract/${id}`,
        method: "PUT",
        body: contractData,
      }),
      invalidatesTags: ["Contracts", "ContractDetails"],
    }),
    deleteContract: builder.mutation({
      query: (id) => ({
        url: `/crscan/contract/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Contracts"],
    }),
  }),
});

export const {
  useFetchContractsQuery,
  useFetchContractDetailsQuery,
  useAddContractMutation,
  useUpdateContractMutation,
  useDeleteContractMutation,
} = contractApi;
