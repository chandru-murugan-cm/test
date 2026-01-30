from google.cloud import scheduler_v1
from google.protobuf import duration_pb2
from google.protobuf import timestamp_pb2
from datetime import datetime, timezone, timedelta
import json
import uuid
from dotenv import load_dotenv
import os
from google.cloud import scheduler_v1
import base64

load_dotenv()
scheduler_key = os.getenv('SCHEDULER_SECRET_KEY')
scheduler_timezone = os.getenv('SCHEDULER_TIMEZONE')
scheduler_api_endpoint = os.getenv('SCHEDULER_API_ENDPOINT')

# Function to create a job in Google Cloud Scheduler
def create_cloud_scheduler_job(project_id, location, cron_schedule, payload, schedule_id):
    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{project_id}/locations/{location}"
    job = {
        "name": f"{parent}/jobs/{schedule_id}",  # Unique job ID
        "schedule": cron_schedule,
        "time_zone": scheduler_timezone,   # Adjust this as needed
        "http_target": {
            "http_method": scheduler_v1.HttpMethod.POST,
            "uri": scheduler_api_endpoint,  # Your API endpoint for running scans
            "headers": {
                "Content-Type": "application/json",
                "X-Scheduler-Secret": scheduler_key
            },
            "body": json.dumps(payload).encode()  # The request body containing scan info
        }
    }

    # Create the job
    response = client.create_job(request={"parent": parent, "job": job})
    schedule_details = get_cloud_scheduler_job_details(project_id, location, schedule_id)
    return schedule_details

# Function to generate a cron expression based on the user's selected schedule
def generate_cron_expression(options, time=None, day=None, date=None):
    """
    Generates a cron expression based on the options:
    - Daily: Runs every day at the specified time
    - Weekly: Runs every week on the specified day and time
    - Monthly: Runs every month on the specified date and time
    """
    cron_schedule = ""

    if options == "daily":
        # Run daily at the specified time (e.g., 09:30 every day)
        cron_schedule = f"{time.minute} {time.hour} * * *"
    
    elif options == "weekly":
        # Run weekly on the specified day (0 = Sunday, 6 = Saturday) and time
        cron_schedule = f"{time.minute} {time.hour} * * {day}"

    elif options == "monthly":
        # Run monthly on the specified date (1-31) and time
        cron_schedule = f"{time.minute} {time.hour} {date} * *"

    return cron_schedule

def get_cloud_scheduler_job_details(project_id, location, schedule_id):
    client = scheduler_v1.CloudSchedulerClient()
    job_name = f"projects/{project_id}/locations/{location}/jobs/{schedule_id}"

    try:
        job = client.get_job(name=job_name)

        # Extract headers from the job's HTTP target (already a dictionary)
        headers = {k: v for k, v in job.http_target.headers.items()}

        # Base64 encode the body to match the format in your example
        body = base64.b64encode(job.http_target.body).decode('utf-8')

        # Handle DatetimeWithNanoseconds objects using the timestamp() method
        if job.schedule_time:
            schedule_time = datetime.fromtimestamp(job.schedule_time.timestamp(), tz=timezone.utc).isoformat()
        else:
            schedule_time = None

        if job.user_update_time:
            user_update_time = datetime.fromtimestamp(job.user_update_time.timestamp(), tz=timezone.utc).isoformat()
        else:
            user_update_time = None

        # Build the desired job details JSON structure
        job_details = {
            "name": job.name,
            "httpTarget": {
                "uri": job.http_target.uri,
                "httpMethod": job.http_target.http_method.name,
                "headers": headers,
                "body": body
            },
            "userUpdateTime": user_update_time if user_update_time else None,
            "state": job.state.name,
            "scheduleTime": schedule_time if schedule_time else None,
            "schedule": job.schedule,
            "timeZone": job.time_zone,
            "attemptDeadline": f"{job.attempt_deadline.seconds}s" if job.attempt_deadline else None
        }

        return {"success": "Job details retrieved successfully", "data": job_details}

    except Exception as e:
        return {"error": f"Failed to retrieve job details: {str(e)}"}