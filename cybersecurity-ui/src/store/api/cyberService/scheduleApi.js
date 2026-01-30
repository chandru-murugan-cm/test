// src/services/cyberServiceApi.js
import { createApi } from "@reduxjs/toolkit/query/react";
import customBaseQuery from "../customBaseQuery";

export const schedulesApi = createApi({
  reducerPath: "schedulesApi",
  baseQuery: customBaseQuery,
  endpoints: (builder) => ({
    fetchSchedules: builder.query({
      query: (projectId) => ({ url: `/cs/scheduler?project_id=${projectId}` }),
      providesTags: ["Schedules"],
    }),
    addSchedule: builder.mutation({
      query: (scheduleData) => ({
        url: "/cs/scheduler",
        method: "POST",
        body: scheduleData,
      }),

      invalidatesTags: (result, error, { projectId }) => [
        // Invalidate the schedules cache
        { type: "Schedules", id: projectId },
        // Invalidate the scans cache for the project
        { type: "Scans", id: projectId },
      ],
    }),
    editSchedule: builder.mutation({
      query: ({ id, scheduleData }) => ({
        url: `/cs/scheduler/${id}`,
        method: "PUT",
        body: scheduleData,
      }),
      invalidatesTags: ["Schedules"],
    }),
    deleteSchedule: builder.mutation({
      query: ({ id }) => ({
        url: `/cs/scheduler/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Schedules"],
    }),
    scanNow: builder.mutation({
      query: (scanData) => ({
        url: "/cs/scheduler/scanNow",
        method: "POST",
        body: scanData,
      }),
      invalidatesTags: (result, error, { projectId }) => [
        // Invalidate the schedules cache
        { type: "Schedules", id: projectId },
        // Invalidate the scans cache for the project
        { type: "Scans", id: projectId },
      ],
    }),
  }),
});

export const {
  useFetchSchedulesQuery,
  useAddScheduleMutation,
  useEditScheduleMutation,
  useDeleteScheduleMutation,
  useScanNowMutation,
} = schedulesApi;
