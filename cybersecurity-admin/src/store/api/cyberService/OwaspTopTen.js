import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const owaspTopTenApi = createApi({
  reducerPath: "owaspTopTenApi",
  baseQuery: customBaseQuery,
  tagTypes: ["OwaspTopTen"],
  endpoints: (builder) => ({
    fetchOwaspTopTen: builder.query({
      query: (owasp_top_ten_id) => ({
        url: owasp_top_ten_id
          ? `/crscan/owasp_top_ten?owasp_top_ten_id=${owasp_top_ten_id}`
          : "/crscan/owasp_top_ten",
        method: "GET",
      }),
      providesTags: ["OwaspTopTen"],
    }),

    addOwaspTopTen: builder.mutation({
      query: (newOwaspTopTen) => ({
        url: "/crscan/owasp_top_ten",
        method: "POST",
        body: newOwaspTopTen, 
      }),
      invalidatesTags: ["OwaspTopTen"],
    }),

    updateOwaspTopTen: builder.mutation({
      query: ({ owasp_top_ten_id, updatedData }) => ({
        url: `/crscan/owasp_top_ten/${owasp_top_ten_id}`,
        method: "PUT",
        body: updatedData,
      }),
      invalidatesTags: ["OwaspTopTen"],
    }),
    
    deleteOwaspTopTen: builder.mutation({
      query: (owasp_top_ten_id) => ({
        url: `/crscan/owasp_top_ten/${owasp_top_ten_id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["OwaspTopTen"],
    }),
    
  }),
});

export const {
  useFetchOwaspTopTenQuery,
  useAddOwaspTopTenMutation,
  useUpdateOwaspTopTenMutation,
  useDeleteOwaspTopTenMutation,
} = owaspTopTenApi;
