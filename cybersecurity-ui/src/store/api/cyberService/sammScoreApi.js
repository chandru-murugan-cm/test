import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const sammUserScoreApi = createApi({
  reducerPath: "sammUserScoreApi",
  baseQuery: customBaseQuery,
  tagTypes: ["SammUserScore"],
  endpoints: (builder) => ({
    fetchScores: builder.query({
      query: ({ projectId }) => ({
        url: `/crscan/samm-scores?project_id=${projectId}`,
        method: "GET",
      }),
      providesTags: ["SammUserScore"],
    }),
    addOrUpdateScore: builder.mutation({
      query: (scoreData) => ({
        url: "/crscan/samm-scores",
        method: "POST",
        body: scoreData,
      }),
      invalidatesTags: ["SammUserScore"],
    }),
  }),
});

export const { useFetchScoresQuery, useAddOrUpdateScoreMutation } =
  sammUserScoreApi;
