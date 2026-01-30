import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const vaptReportApi = createApi({
    reducerPath: "vaptReportApi",
    baseQuery: customBaseQuery,
    tagTypes: ["VaptReport"],
    endpoints: (builder) => ({
        fetchVaptReports: builder.query({
            query: ({ project_id, user_id, year, month } = {}) => {
                const params = new URLSearchParams();
                if (project_id) params.append("project_id", project_id);
                if (user_id) params.append("user_id", user_id);
                if (year) params.append("year", year);
                if (month) params.append("month", month);
                return {
                    url: `/crscan/vapt-reports?${params.toString()}`,
                    method: "GET",
                };
            },
            providesTags: ["VaptReport"],
        }),
    }),
});

export const { useFetchVaptReportsQuery } = vaptReportApi;
