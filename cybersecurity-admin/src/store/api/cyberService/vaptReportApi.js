import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const vaptReportApi = createApi({
    reducerPath: "vaptReportApi",
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
    tagTypes: ["VaptReport", "ManualVaptFindings"],
    endpoints: (builder) => ({
        uploadVaptReport: builder.mutation({
            query: (reportData) => ({
                url: "/crscan/vapt-reports",
                method: "POST",
                body: reportData,
            }),
            invalidatesTags: ["VaptReport"],
        }),
        fetchVaptReports: builder.query({
            query: ({ project_id, user_id, year, month } = {}) => {
                const params = new URLSearchParams();
                if (project_id) params.append("project_id", project_id);
                if (user_id) params.append("user_id", user_id);
                if (year) params.append("year", year);
                if (month) params.append("month", month);
                const qs = params.toString();
                return `/crscan/vapt-reports${qs ? `?${qs}` : ""}`;
            },
            providesTags: ["VaptReport"],
        }),
        updateVaptReport: builder.mutation({
            query: ({ vapt_report_id, reportData }) => ({
                url: `/crscan/vapt-reports/${vapt_report_id}`,
                method: "PUT",
                body: reportData,
            }),
            invalidatesTags: ["VaptReport"],
        }),
        deleteVaptReport: builder.mutation({
            query: (vapt_report_id) => ({
                url: `/crscan/vapt-reports/${vapt_report_id}`,
                method: "DELETE",
            }),
            invalidatesTags: ["VaptReport"],
        }),
        fetchAllProjects: builder.query({
            query: () => "/crscan/vapt-reports/all-projects",
        }),
        fetchAllUsers: builder.query({
            query: () => "/crscan/vapt-reports/all-users",
        }),
        fetchUserProjects: builder.query({
            query: (userId) => `/crscan/vapt-reports/user-projects/${userId}`,
        }),
        uploadManualVaptJson: builder.mutation({
            query: (formData) => ({
                url: "/crscan/manual-vapt-upload",
                method: "POST",
                body: formData,
            }),
            invalidatesTags: ["VaptReport"],
        }),
        validateManualVaptJson: builder.mutation({
            query: (formData) => ({
                url: "/crscan/manual-vapt-upload/validate",
                method: "POST",
                body: formData,
            }),
        }),
        fetchManualVaptFindings: builder.query({
            query: ({ project_id, user_id, severity, status, target_type, year, month } = {}) => {
                const params = new URLSearchParams();
                if (project_id) params.append("project_id", project_id);
                if (user_id) params.append("user_id", user_id);
                if (severity) params.append("severity", severity);
                if (status) params.append("status", status);
                if (target_type) params.append("target_type", target_type);
                if (year) params.append("year", year);
                if (month) params.append("month", month);
                const qs = params.toString();
                return `/crscan/manual-vapt-upload/findings${qs ? `?${qs}` : ""}`;
            },
            providesTags: ["ManualVaptFindings"],
        }),
        updateManualVaptFinding: builder.mutation({
            query: ({ finding_id, data }) => ({
                url: `/crscan/manual-vapt-upload/findings/${finding_id}`,
                method: "PUT",
                body: data,
            }),
            invalidatesTags: ["ManualVaptFindings"],
        }),
        deleteManualVaptFinding: builder.mutation({
            query: (finding_id) => ({
                url: `/crscan/manual-vapt-upload/findings/${finding_id}`,
                method: "DELETE",
            }),
            invalidatesTags: ["ManualVaptFindings"],
        }),
    }),
});

export const {
    useUploadVaptReportMutation,
    useFetchVaptReportsQuery,
    useUpdateVaptReportMutation,
    useDeleteVaptReportMutation,
    useFetchAllProjectsQuery,
    useFetchAllUsersQuery,
    useFetchUserProjectsQuery,
    useUploadManualVaptJsonMutation,
    useValidateManualVaptJsonMutation,
    useFetchManualVaptFindingsQuery,
    useUpdateManualVaptFindingMutation,
    useDeleteManualVaptFindingMutation,
} = vaptReportApi;
