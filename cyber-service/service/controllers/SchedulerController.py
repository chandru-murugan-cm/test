import os
from controllers.util import *
from entities.CyberServiceEntity import Project, Scanners, ScannerTypes,Scheduler, FindingLicensesAndSbom, RawScanOutput, FindingMaster, RepoSecretDetections
from typing import List
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from mongoengine import *
from marshmallow import Schema, fields, ValidationError, INCLUDE
from datetime import datetime, timezone, timedelta
import pytz
import uuid
import json
import shutil
import tempfile
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures
from bson import ObjectId
from openai import OpenAI
from entities.CyberServiceEntity import Project, Scanners, Scheduler,Scans
import subprocess
from .utility.zap.zap_scanner import run_zap_scan
# from .utility.trivy.TrivyScanner import TrivyScanner
from .ScansController import ScansController
from .utility.googleCloudScheduler import create_cloud_scheduler_job, generate_cron_expression

from controllers.RepositoryController import RepositoryProvider

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')

gcp_project_id = os.getenv('GCP_PROJECT_ID')
gcp_location = os.getenv('GCP_LOCATION')


# Set your OpenAI API key
client = OpenAI(api_key=openai_api_key)

# trivyScanner = TrivyScanner()
scancontroller_obj = ScansController()

class SchedulerAddSchema(Schema):
    project_id = fields.String(required=True, error_messages={
        "required": "Project ID is required."})
    
    options = fields.String(required=True, error_messages={
        "required": "Options is required."})
    scanner_type_ids_list = fields.List(fields.String(), required=True, error_messages={
        "required": "Scanner IDs list is required."})
    


class SchedulerUpdateSchema(Schema):
    scheduler_id = fields.String(required=True, error_messages={
        "required": "Scheduler ID is required."})
    project_id = fields.String(required=True, error_messages={
        "required": "Project ID is required."})
    # scanner_id = fields.String(required=True, error_messages={
    #     "required": "Scanner ID is required."})
    options = fields.String(required=True, error_messages={
        "required": "Options is required."})
    scanner_type_ids_list= fields.List(fields.String(), required=True, error_messages={
        "required": "Scanner IDs list is required."})
   


class SchedulerController:
    """
    Defines controller methods for the Scheduler Entity.
    """

    def __init__(self) -> None:
        pass

    def run_command(self, command, cwd=None):
        try:
            output = subprocess.check_output(
                command, shell=True, text=True, cwd=cwd, stderr=subprocess.STDOUT
            )
            return output
        except subprocess.CalledProcessError as e:
            return f"Error running command: {str(e)}. Output: {e.output}"

    def clone_github_repo(self, repo_url, access_token, repository_provider):
        temp_dir = tempfile.mkdtemp()

        if access_token is not None:
            if repository_provider == RepositoryProvider.GITLAB.value:
                repo_url = repo_url.replace("gitlab.com", f"oauth2:{access_token}@gitlab.com")
            elif repository_provider == RepositoryProvider.GITHUB.value:
                repo_url = repo_url.replace("github.com", f"{access_token}@github.com")

        clone_command = f"git clone {repo_url} {temp_dir}"
        clone_output = self.run_command(clone_command)

        git_dir = os.path.join(temp_dir, ".git")
        if not os.path.exists(git_dir):
            shutil.rmtree(temp_dir)
            return None, f"Error: {clone_output}. Git repository not found."

        if "Error" in clone_output:
            shutil.rmtree(temp_dir)
            return None, clone_output

        return temp_dir, clone_output
    def _validateSchedulerAdd(self, request_json):
        schema = SchedulerAddSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'validation successful'}, '200 Ok'

    def _validateSchedulerUpdate(self, request_json):
        schema = SchedulerUpdateSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'validation successful'}, '200 Ok'

    def _validateScheduler(self, scheduler_id):
        """
        Validates scheduler id with database
        """
        try:
            Scheduler.objects.get(scheduler_id=scheduler_id)
            return True, {'message': 'Record exists in db'}, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_schedules(self, request, fields):
        # Fetch the current user
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Validate project_id
        project_id = fields.get('project_id')
        if not project_id:
            return jsonify({"error": "Missing 'project_id' in request"}), 400

        # Fetch scheduler details
        scheduler_details = list(Scheduler.objects(project_id=project_id))
        if not scheduler_details:
            return jsonify({"success": "No schedulers found", "data": []}), 200

        # Collect scanner IDs
        scanner_ids = set()
        scanner_type_ids = set()
        for scheduler in scheduler_details:
            if 'scanner_ids_list' in scheduler:
                scanner_ids.update(scheduler['scanner_ids_list'])
            if 'scanner_type_ids_list' in scheduler:
                scanner_type_ids.update(scheduler['scanner_type_ids_list'])
        
        # Fetch scanner details
        scanner_ids = list(scanner_ids)
        scanner_type_ids = list(scanner_type_ids)

        # Get unique scanner types
        unique_types = []
        if scanner_ids:
            scanner_details = Scanners.objects.filter(scanner_id__in=scanner_ids)
            all_types = set()
            for scanner in scanner_details:
                if scanner.type:
                    if isinstance(scanner.type, list):
                        all_types.update(scanner.type)
                    else:
                        all_types.add(scanner.type)
            unique_types = list(all_types)

        # Fetch ScannerTypes details
        scanner_types_map = {}
        if scanner_type_ids:
            scanner_types = ScannerTypes.objects.filter(scan_type_id__in=scanner_type_ids)
            scanner_types_map = {str(scanner.id): scanner.to_mongo().to_dict() for scanner in scanner_types}

        # Prepare the final response
        for i, scheduler in enumerate(scheduler_details):
            scheduler_dict = scheduler.to_mongo().to_dict()
            scheduler_dict['unique_scanner_types'] = unique_types
            
            # Add scanner type details
            scanner_type_details = []
            if 'scanner_type_ids_list' in scheduler_dict:
                for scanner_type_id in scheduler_dict['scanner_type_ids_list']:
                    if scanner_type_id in scanner_types_map:
                        scanner_type_details.append(scanner_types_map[scanner_type_id])
            
            scheduler_dict['scanner_type_details'] = scanner_type_details

            # Check if the schedule is daily and add nextScanTime
            if scheduler_dict.get('options') == 'daily' and scheduler_dict.get('next_run'):
                next_run_time = scheduler_dict['next_run']

                # If next_run_time is already a datetime object, use it directly
                if isinstance(next_run_time, datetime):
                    next_run_dt = next_run_time
                    # Ensure it's a timezone-aware datetime (in UTC)
                    if next_run_dt.tzinfo is None:
                        next_run_dt = pytz.utc.localize(next_run_dt)
                else:
                    # If it's a string, parse it and localize to UTC
                    next_run_dt = datetime.strptime(next_run_time, "%a, %d %b %Y %H:%M:%S GMT")
                    # Ensure it's a timezone-aware datetime (in UTC)
                    next_run_dt = pytz.utc.localize(next_run_dt)

                # Get current time in UTC and ensure it's timezone-aware
                current_time = datetime.now(pytz.utc)  # Make current_time aware
                print(current_time, "current")
                print(next_run_dt, "nextRun")
                next_run_time_only = next_run_dt.time()

                # Ensure both times are timezone-aware before comparison
                if current_time > next_run_dt:
                    # Set next_scan_time to the same time as next_run_dt but on the next day
                    next_scan_time = datetime.combine(current_time.date() + timedelta(days=1), next_run_time_only)
                    next_scan_time = pytz.utc.localize(next_scan_time)  # Ensure it's timezone-aware
                else:
                    # If the time hasn't passed yet, use today's date with the time from next_run_dt
                    next_scan_time = datetime.combine(current_time.date(), next_run_time_only)
                    next_scan_time = pytz.utc.localize(next_scan_time)  

                # Add the nextScanTime field to the scheduler data
                scheduler_dict['next_scan_time'] = next_scan_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            scheduler_details[i] = scheduler_dict

        # Return the response
        return jsonify({"success": "Scheduler fetched successfully", "data": scheduler_details}), 200




    def update_by_id(self, request_json) -> dict:
        """
        Fetches and updates a scheduler object by its ID.
        """
        # Fetching user ID from JWT token and validate the token
        current_user = get_current_user_from_jwt_token()

        # Parse the request JSON
        request_json = request.get_json()
        
        # Validate scheduler update request
        status, result, status_code = self._validateSchedulerUpdate(request_json)
        if not status:
            return jsonify(result), status_code

        scheduler_id = request_json.get('scheduler_id')
        if not scheduler_id or not scheduler_id.strip():
            return {'error': 'Scheduler ID is required'}, '400 Bad Request'

        # Validate the scheduler ID
        status, result, status_code = self._validateScheduler(scheduler_id)
        if not status:
            return result, status_code

        # Extract optional fields
        project_id = request_json.get('project_id')
        options = request_json.get('options')
        scanner_names_list = request_json.get('scanner_ids_list')
        day = request_json.get('day')  # For weekly schedules
        date = request_json.get('date')  # For monthly schedules
        time = request_json.get('time')  # For daily/weekly/monthly schedules

       

        try:
            # Fetch the scheduler object
            scheduler_obj = Scheduler.objects.get(scheduler_id=scheduler_id)

            if scanner_names_list:
                scheduler_obj['scanner_names_list'] = scanner_names_list
                # Aggregation pipeline to find all scanners whose "type" or "name" matches any value in the scanner_names_list
                pipeline = [
                    {"$match": {"type": {"$in": scanner_names_list}}},
                    {"$project": {"scanner_id": 1, "name": 1}}  # Project the scanner_id and name fields
                ]
                # Execute the aggregation pipeline
                result = list(Scanners.objects.aggregate(pipeline))
                
                # Extract the scanner_ids from the result
                scanner_ids_mapped = [str(scanner["_id"]) for scanner in result]

                # If no scanners are found, return an error
                if not scanner_ids_mapped:
                    return {'error': 'No matching scanners found'}, '404 Not Found'

                # Update the scanner_ids_list with the mapped scanner ids
                scheduler_obj['scanner_type_ids_list'] = scanner_ids_mapped

            # Update the scheduler fields
            if project_id:
                scheduler_obj['project_id'] = project_id
            if options:
                scheduler_obj['options'] = options
            if day:
                scheduler_obj['day'] = day
            if date:
                scheduler_obj['date'] = date
            if time:
                try:
                    scheduler_obj['time'] = time
                    
                except ValueError:
                    return {'error': 'Invalid time format. Use HH:mm.'}, '400 Bad Request'

            # Add metadata
            scheduler_obj['updator'] = current_user
            scheduler_obj['updated'] = datetime.now(timezone.utc)

            # Save the updated scheduler
            scheduler_obj.save()

            response = json.loads(scheduler_obj.to_json())
            return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Scheduler not found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'

    def add_entity(self, request_json) -> dict:
        """
        Creates new scheduler obj in the database and creates a Cloud Scheduler job if necessary
        """
        current_user = get_current_user_from_jwt_token()
        request_json = request.get_json()
        project_id = request_json.get('project_id', None)
        options = request_json.get('options', None)
        time = request_json.get('time')  # HH:mm format for time
        day = request_json.get('day')  # Day of the week for weekly option (0 = Sunday)
        date = request_json.get('date')  # Date of the month for monthly option (1-31)
        schedule_date = request_json.get('schedule_date', None)
        scanner_type_ids_list = request_json.get('scanner_type_ids_list', [])
    
        response = {}

        try:
            if options in ["daily", "weekly", "monthly"] and not time:
                return {"error": "Time is required for scheduling"}, 400

            # Parse the time if provided
            schedule_time = datetime.strptime(time, "%H:%M").time()

            # Create the Scheduler object in the database
            new_schedule_obj = Scheduler(
                scheduler_id=str(uuid.uuid4()),
                project_id=project_id,
                status="init",
                options=options,
                time=time,
                day=day,
                date=date,
                schedule_date=datetime.now(timezone.utc),
                scanner_type_ids_list=scanner_type_ids_list,
                next_run=None,
                created=datetime.now(timezone.utc),
                creator=current_user
            )
            new_schedule_obj.save()
            response = json.loads(new_schedule_obj.to_json())
            schedule_id = response.get('_id')
            # If the user didn't select 'scanNow', create a Google Cloud Scheduler job
            if options != "scanNow":
                # Generate cron expression based on the selected schedule
                cron_expression = generate_cron_expression(options, schedule_time, day, date)

                # Define payload for scan execution
                payload = {
                    "scheduler_id": new_schedule_obj.scheduler_id,
                    "scan_type": options,
                    "project_id": project_id,
                    "scanner_type_ids_list": scanner_type_ids_list
                }

                # Create the Cloud Scheduler job
                cloud_scheduler_response = create_cloud_scheduler_job(
                    project_id=gcp_project_id,  # Replace with your GCP Project ID
                    location=gcp_location,  # Replace with your GCP location
                    cron_schedule=cron_expression,
                    payload=response,
                    schedule_id=schedule_id
                )
                gcp_sch_details = cloud_scheduler_response.get('data')
                # schedule_time = gcp_sch_details.get('scheduleTime')
                schedule_time = datetime.strptime(gcp_sch_details.get('scheduleTime'), "%Y-%m-%dT%H:%M:%S.%f%z")
                sch_obj = Scheduler.objects.get(scheduler_id=schedule_id)
                sch_obj['next_run'] = schedule_time
                sch_obj.save()
                response = json.loads(sch_obj.to_json())
                print(json.loads(sch_obj.to_json()))
                print(f"Cloud Scheduler job created: {cloud_scheduler_response}")
            else:
                scan_request_json = {
                    "scheduler_response": response,
                    "scan_status":"running"
                }
                scancontroller_obj.add_entity(scan_request_json)
        except Exception as e:
            return {'error': f'Internal Server Error: {str(e)}'}, '500 Internal Server Error'

        return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'

    def remove_entity(self, scheduler_id):
        """
        Removes the Scheduler object from the database.
        """
        # Validates the JWT Token
        verify_jwt_in_request()
        try:
            scheduler_obj = Scheduler.objects.get(
                scheduler_id=scheduler_id)
            scheduler_obj.soft_delete()
            return {'success': 'Record Deleted Successfully'}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def run_scan(self, schedule_details, scanner_names_mapped, scanner_ids_length, current_user):
        print("Inside scanner.....", schedule_details)
        print("schedule_id", type(schedule_details.get('_id', None)))
        try:
            project_id = schedule_details.get('project_id', None)
            project_obj = Project.objects.get(project_id=project_id)
            project_details = json.loads(project_obj.to_json())
            print("project_details", project_details)
            print("project_obj", project_obj)
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        domain = project_details.get("domain_value", None)
        repo_url = project_details.get("repo_url", None)
        access_token = project_details.get("access_token", None)
        repository_provider = project_details.get("repository_provider", None)
        scheduler_id = schedule_details['_id']
        print("scheduler_id", type(scheduler_id))
        print("access_token", access_token)
        
        repo_path, clone_output = self.clone_github_repo(repo_url, access_token, repository_provider)
        if not repo_path:
            print("clone_output" , clone_output)
            return None, f"Failed to clone repository: {clone_output}"
        
        try:
            print(domain, repo_url, scheduler_id)
            new_unformatted_scan_result_obj = Unformatted_scan_results(
                unformatted_scan_results_id=str(uuid.uuid4()),
                scheduler_id=scheduler_id,
                project_id=project_id,
                created=datetime.now(timezone.utc),
                creator=current_user
            )
            print("new_unformatted_scan_result_obj")
            new_unformatted_scan_result_obj.save()
            new_unformatted_scan_result_response = json.loads(
                new_unformatted_scan_result_obj.to_json())
            print('new_unformatted_scan_result_response',
                new_unformatted_scan_result_response)
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        raw_scan_output_id = new_unformatted_scan_result_response.get("_id")

        scan_futures = []
        with ThreadPoolExecutor() as executor:
            # Submit scanner tasks based on scanner_names_mapped
            if 'Amass' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_amass, raw_scan_output_id, domain, current_user, scanner_ids_length))
            if 'Nmap' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_nmap, raw_scan_output_id, domain, current_user, scanner_ids_length))
            if 'Whois' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_whois, raw_scan_output_id, domain, current_user, scanner_ids_length))
            if 'Linguist' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_linguist, raw_scan_output_id, repo_path, current_user, scanner_ids_length))
            if 'Zap' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_zap, raw_scan_output_id, domain, repo_url, current_user, scanner_ids_length))
            if 'GitLeaks' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_gitleaks, raw_scan_output_id, repo_path, current_user, scanner_ids_length))
            if 'Trivy' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_trivy, raw_scan_output_id, repo_path, current_user, scanner_ids_length))
            if 'Doggo' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_doggo, raw_scan_output_id, domain, current_user, scanner_ids_length))
            if 'Wapiti' in scanner_names_mapped:
                scan_futures.append(executor.submit(
                    self.run_wapiti, raw_scan_output_id, domain, current_user, scanner_ids_length))
            # if 'Nikto' in scanner_names_mapped:
            #     scan_futures.append(executor.submit(
            #         self.run_nikto, raw_scan_output_id, domain, current_user, scanner_ids_length))

        # # Wait for all submitted scans to complete
        # for future in as_completed(scan_futures):
        #     try:
        #         result = future.result()
        #         print(f"Scan result: {result}")
        #     except Exception as e:
        #         print(f"An error occurred during the scan: {e}")

        # return {'success': 'Scan tasks submitted successfully'}, '200 Ok'

        self.cleanup_repo(raw_scan_output_id, repo_url)

        # Update status and add updated time and updator
        unformatted_scan_obj = Unformatted_scan_results.objects.get(unformatted_scan_results_id=raw_scan_output_id)

        # Update the required fields
        unformatted_scan_obj.status = "completed"
        unformatted_scan_obj.updated = datetime.now(timezone.utc)
        unformatted_scan_obj.updator = get_current_user_from_jwt_token()['id']

        # Save the updates to the database
        unformatted_scan_obj.save()


    def increment_scan_status(self, raw_scan_output_id, scanner_ids_length):
        # Fetch the job document from the Unformatted_scan_results collection
        job = Unformatted_scan_results.objects.get(unformatted_scan_results_id=raw_scan_output_id)

        # If the job is not found, handle the error
        if not job:
            print(f"No job found with ID: {raw_scan_output_id}")
            return

        # Get the current status and parse the completed and total values
        current_status = job.scans_status if job.scans_status else f"0/{scanner_ids_length}"
        completed, total = map(int, current_status.split("/"))

        # Increment the completed count and update the status string
        new_completed = completed + 1
        new_status = f"{new_completed}/{scanner_ids_length}"

        # Update the job object with the new scan status
        job.scans_status = new_status
        job.updated = datetime.now(timezone.utc)
        job.save()

        print(f"Updated scan status for {raw_scan_output_id}: {new_status}")


    def run_amass(self, unformatted_scan_results_id, domain, current_user, scanner_ids_length):
        print("running amass....")
        amass_output = os.popen(f"amass enum -d {domain}").read()
        try:
            unformatted_scan_results_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_results_id)
            unformatted_scan_results_obj['amass'] = amass_output
            unformatted_scan_results_obj['updator'] = current_user
            unformatted_scan_results_obj['updated'] = datetime.now(
                timezone.utc)
            unformatted_scan_results_obj.save()
            print("unformatted scan result", unformatted_scan_results_obj)
            unformatted_scan_results_details = json.loads(
                unformatted_scan_results_obj.to_json())
            # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        print("amass completed")
        # Prepare the prompt for the AI model with specified columns
        prompt = f"""
        Given the following raw Amass scan output, extract all the key information and convert it into a structured format:
        Raw Scan Output:
        {amass_output}

        Desired Structured Format:
        [
            {{
                "findings": "",  # Extract specific vulnerabilities, discovered domains, or key issues from the scan
                "issue_detail": "",  # Provide details on the issue identified, describing how it was detected, any error messages returned, or other evidence of the vulnerability
                "issue_background": "",  # Explain the technical background and implications of the issue, including common causes and possible attack scenarios, similar to SQL injection example
                "issue_remediation": "",  # Recommend effective steps to fix or mitigate the issue, including best practices and specific configuration or coding practices to avoid it
                "references": "",  # List relevant resources, such as security articles, cheat sheets, or tool documentation, to guide on further investigation or mitigation
                "vulnerability_classifications": "",  # Provide vulnerability classification codes, like CWE or CAPEC, that relate to the issue for easy reference
                "target": "{domain}",  # The target domain being scanned
                "status": "Open",  # Vulnerabilities or issues should default to "Open"
                "risk_level": "",  # Assess the severity of any findings based on Amass output (high, medium, low, critical)
                "severity_range": 0,  # A single integer between 1 and 100 representing severity
                "source_scanners": "Amass",  # Set to "Amass" since this is an Amass DNS scan
                "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # Date when the scan was conducted
                "additional_info": ""  # Any additional information like IP addresses, DNS records, etc.
            }},
            ...
        ]

        Please ensure:
        - "findings" contains relevant issues such as discovered subdomains, DNS records, IP addresses, or related network information.
        - "risk_level" is assigned based on potential risks such as misconfigurations, domain exposure, or vulnerabilities.
        - Return the result **strictly as a raw JSON array without any additional text or formatting**.
        """


        # Call the OpenAI API to get the structured output
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                         messages=[
                                                             {"role": "user", "content": prompt}],
                                                         temperature=0.7)
        print("response", response)

        structured_results = response.choices[0].message.content
        print("structured_results", structured_results)

        cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        # Ensure the cleaned results are valid JSON
        try:
            json_data = json.loads(cleaned_results)
            print("json_data",json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        # After obtaining the structured_results from the OpenAI response


        # Iterate through each finding in the structured results and save to the database
        for result in json_data:
            print("result", result)
            print("result", type(result))
            print("finding",result.get('findings', ''))
            print("target",result.get('target', ''))
            print("risk_level",result.get('risk_level', ''))
            print("source_scanners",result.get('source_scanners', ''))
            print("scan_date",result.get('scan_date', ''))
            print("additional_info",result.get('additional_info', ''))
            additional_info_value = result.get('additional_info', '')
            if not isinstance(additional_info_value, str):
                additional_info_value = str(additional_info_value)
            finding = result.get('findings', '')
            if not isinstance(finding, str):
                finding_value = str(finding)
            else:
                finding_value = finding
            try:
                new_refined_scan_obj = Refined_scan_results(
                    refined_scan_results_id=str(uuid.uuid4()),  # Generate a new unique ID for each record
                    unformatted_scan_results_id=unformatted_scan_results_id,  # Reference the unformatted scan
                    finding=finding_value,  # Extract the 'findings' from the result
                    issue_detail=result.get('issue_detail', ''),  
                    issue_background=result.get('issue_background', ''),  
                    issue_remediation=result.get('issue_remediation', ''),  
                    references=result.get('references', ''),  
                    vulnerability_classifications=result.get('vulnerability_classifications', ''), 
                    target=result.get('target', ''),  # Extract the 'target' from the result
                    severity=result.get('risk_level', ''),  # Extract the 'risk_level' as severity
                    severity_range=result.get('severity_range', ''), # Extract the 'severity_range' from the result
                    scan_status=result.get('status', ''), # Extract the 'status' from the result as scan_status
                    scanner=result.get('source_scanners', ''),  # Use 'ZAP' as the scanner
                    scan_date=result.get('scan_date', ''),  # Extract the 'scan_date'
                    additional_info=additional_info_value,  # Extract 'additional_info'
                    created=datetime.now(timezone.utc),  # Set the creation date to current time
                    creator=current_user  # Set the user creating this entry
                )
                
                new_refined_scan_obj.save()  # Save the record into the database
                print("response", json.loads(new_refined_scan_obj.to_json()))
                # print(f"Saved refined scan result: {new_refined_scan_obj}")
            except Exception as e:
                print("errorroror", e)
                print(f"Unexpected error occurred while saving: {e}")
            # except DoesNotExist as e:
            #     print("error",e)
            #     return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            # except ValidationError as e:
            #     print("verror",e)
            #     return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)

    def run_nmap(self, unformatted_scan_results_id, domain, current_user, scanner_ids_length):
        print("running nmap....")
        nmap_output = os.popen(f"nmap {domain}").read()
        try:
            unformatted_scan_results_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_results_id)
            unformatted_scan_results_obj['nmap'] = nmap_output
            unformatted_scan_results_obj['updator'] = current_user
            unformatted_scan_results_obj['updated'] = datetime.now(
                timezone.utc)
            unformatted_scan_results_obj.save()
            print("unformatted scan result", unformatted_scan_results_obj)
            unformatted_scan_results_details = json.loads(
                unformatted_scan_results_obj.to_json())
            # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        print("nmap completed")

        # Prepare the prompt for the AI model with specified columns
        prompt = f"""
        Given the following raw Nmap scan output, extract all the key information and convert it into a structured format:
        Raw Scan Output:
        {nmap_output}

        Desired Structured Format:
        [
            {{
                "findings": "",  # Key findings from the Nmap scan (e.g., open ports, services, version info, and vulnerabilities)
                "issue_detail": "",  # Provide details on the issue identified, describing how it was detected, any error messages returned, or other evidence of the vulnerability
                "issue_background": "",  # Explain the technical background and implications of the issue, including common causes and possible attack scenarios, similar to SQL injection example
                "issue_remediation": "",  # Recommend effective steps to fix or mitigate the issue, including best practices and specific configuration or coding practices to avoid it
                "references": "",  # List relevant resources, such as security articles, cheat sheets, or tool documentation, to guide on further investigation or mitigation
                "vulnerability_classifications": "",  # Provide vulnerability classification codes, like CWE or CAPEC, that relate to the issue for easy reference
                "target": "{domain}",  # The target domain or IP being scanned
                "status": "Open",  # Defaulted to "Open" for detected issues
                "risk_level": "",  # Assign a risk level based on the open ports, services, and vulnerabilities (high, medium, low, critical)
                "severity_range": 0,  # A single integer between 1 and 100 representing severity
                "source_scanners": "Nmap",  # Set to "Nmap" since this is an Nmap scan
                "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # The date when the scan was conducted
                "additional_info": ""  # Any additional information such as OS detection, versioning, or extra flags from the scan
            }},
            ...
        ]

        Please ensure:
        - "findings" includes key scan details such as open ports, service names, versions, potential vulnerabilities, or OS detection.
        - "risk_level" is based on the nature of open ports and services (e.g., high for critical services, low for less risky ones).
        - Return the result **strictly as a raw JSON array without any additional text or formatting**.
        """


        # Call the OpenAI API to get the structured output
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                         messages=[
                                                             {"role": "user", "content": prompt}],
                                                         temperature=0.7)

        print("response", response)

        structured_results = response.choices[0].message.content
        print("structured_results", structured_results)

        cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        # Ensure the cleaned results are valid JSON
        try:
            json_data = json.loads(cleaned_results)
            print("json_data",json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        # After obtaining the structured_results from the OpenAI response


        # Iterate through each finding in the structured results and save to the database
        for result in json_data:
            print("result", result)
            print("result", type(result))
            print("finding",result.get('findings', ''))
            print("target",result.get('target', ''))
            print("risk_level",result.get('risk_level', ''))
            print("source_scanners",result.get('source_scanners', ''))
            print("scan_date",result.get('scan_date', ''))
            print("additional_info",result.get('additional_info', ''))
            additional_info_value = result.get('additional_info', '')
            if not isinstance(additional_info_value, str):
                additional_info_value = str(additional_info_value)
            finding = result.get('findings', '')
            if not isinstance(finding, str):
                finding_value = str(finding)
            else:
                finding_value = finding
            try:
                new_refined_scan_obj = Refined_scan_results(
                    refined_scan_results_id=str(uuid.uuid4()),  # Generate a new unique ID for each record
                    unformatted_scan_results_id=unformatted_scan_results_id,  # Reference the unformatted scan
                    finding=finding_value,  # Extract the 'findings' from the result
                    issue_detail=result.get('issue_detail', ''),  
                    issue_background=result.get('issue_background', ''),  
                    issue_remediation=result.get('issue_remediation', ''),  
                    references=result.get('references', ''),  
                    vulnerability_classifications=result.get('vulnerability_classifications', ''), 
                    target=result.get('target', ''),  # Extract the 'target' from the result
                    severity=result.get('risk_level', ''),  # Extract the 'risk_level' as severity
                    severity_range=result.get('severity_range', ''), # Extract the 'severity_range' from the result
                    scan_status=result.get('status', ''), # Extract the 'status' from the result as scan_status
                    scanner=result.get('source_scanners', ''),  # Use 'ZAP' as the scanner
                    scan_date=result.get('scan_date', ''),  # Extract the 'scan_date'
                    additional_info=additional_info_value,  # Extract 'additional_info'
                    created=datetime.now(timezone.utc),  # Set the creation date to current time
                    creator=current_user  # Set the user creating this entry
                )
                
                new_refined_scan_obj.save()  # Save the record into the database
                print("response", json.loads(new_refined_scan_obj.to_json()))
                # print(f"Saved refined scan result: {new_refined_scan_obj}")
            except Exception as e:
                print("errorroror", e)
                print(f"Unexpected error occurred while saving: {e}")
            # except DoesNotExist as e:
            #     print("error",e)
            #     return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            # except ValidationError as e:
            #     print("verror",e)
            #     return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)

    def run_whois(self, unformatted_scan_results_id, domain, current_user, scanner_ids_length):
        print("running whois....")
        whois_output = os.popen(f"whois {domain}").read()
        try:
            unformatted_scan_results_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_results_id)
            unformatted_scan_results_obj['whois'] = whois_output
            unformatted_scan_results_obj['updator'] = current_user
            unformatted_scan_results_obj['updated'] = datetime.now(
                timezone.utc)
            unformatted_scan_results_obj.save()
            print("unformatted scan result", unformatted_scan_results_obj)
            unformatted_scan_results_details = json.loads(
                unformatted_scan_results_obj.to_json())
            # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        print("whois completed")

        # Prepare the prompt for the AI model with specified columns
        prompt = f"""
        Given the following raw whois scan output, extract key details and convert it into a structured format:
        Raw Scan Output:
        {whois_output}

        Desired Structured Format:
        [
            {{
                "findings": "",  # Key findings from the Whois scan (e.g., registrar, registration date, expiration date, contact info)
                "issue_detail": "",  # Provide details on the issue identified, describing how it was detected, any error messages returned, or other evidence of the vulnerability
                "issue_background": "",  # Explain the technical background and implications of the issue, including common causes and possible attack scenarios, similar to SQL injection example
                "issue_remediation": "",  # Recommend effective steps to fix or mitigate the issue, including best practices and specific configuration or coding practices to avoid it
                "references": "",  # List relevant resources, such as security articles, cheat sheets, or tool documentation, to guide on further investigation or mitigation
                "vulnerability_classifications": "",  # Provide vulnerability classification codes, like CWE or CAPEC, that relate to the issue for easy reference
                "target": "{domain}",  # The target domain being scanned
                "status": "Open",  # Fixed to "Open" for this case
                "risk_level": "low",  # Default to "low" for Whois unless something critical is found
                "severity_range": 0,  # A single integer between 1 and 100 representing severity
                "source_scanners": "Whois",  # Set to "Whois" since this is a Whois scan
                "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # Date when the scan was conducted
                "additional_info": ""  # Additional Whois-specific data (e.g., name servers, last updated date)
            }},
            ...
        ]

        Please ensure:
        - "findings" includes important Whois data like domain registration, expiration, contact information, and registrar.
        - "risk_level" defaults to low, but can be updated based on sensitive or outdated Whois data if found.
        - Return the result **strictly as a raw JSON array without any additional text or formatting**.
        """


        # Call the OpenAI API to get the structured output
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                         messages=[
                                                             {"role": "user", "content": prompt}],
                                                         temperature=0.7)

        print("response", response)

        structured_results = response.choices[0].message.content
        print("structured_results", structured_results)

        cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        # Ensure the cleaned results are valid JSON
        try:
            json_data = json.loads(cleaned_results)
            print("json_data",json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        # After obtaining the structured_results from the OpenAI response


        # Iterate through each finding in the structured results and save to the database
        for result in json_data:
            print("result", result)
            print("result", type(result))
            print("finding",result.get('findings', ''))
            try:
                new_refined_scan_obj = Refined_scan_results(
                    refined_scan_results_id=str(uuid.uuid4()),  # Generate a new unique ID for each record
                    unformatted_scan_results_id=unformatted_scan_results_id,  # Reference the unformatted scan
                    finding=result.get('findings', ''),  # Extract the 'findings' from the result
                    issue_detail=result.get('issue_detail', ''),  
                    issue_background=result.get('issue_background', ''),  
                    issue_remediation=result.get('issue_remediation', ''),  
                    references=result.get('references', ''),  
                    vulnerability_classifications=result.get('vulnerability_classifications', ''), 
                    target=result.get('target', ''),  # Extract the 'target' from the result
                    severity=result.get('risk_level', ''),  # Extract the 'risk_level' as severity
                    severity_range=result.get('severity_range', ''), # Extract the 'severity_range' from the result
                    scan_status=result.get('status', ''), # Extract the 'status' from the result as scan_status
                    scanner=result.get('source_scanners', 'ZAP'),  # Use 'ZAP' as the scanner
                    scan_date=result.get('scan_date', ''),  # Extract the 'scan_date'
                    additional_info=result.get('additional_info', ''),  # Extract 'additional_info'
                    created=datetime.now(timezone.utc),  # Set the creation date to current time
                    creator=current_user  # Set the user creating this entry
                )
                
                new_refined_scan_obj.save()  # Save the record into the database
                print("response", json.loads(new_refined_scan_obj.to_json()))
                # print(f"Saved refined scan result: {new_refined_scan_obj}")

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)

    def run_linguist(self, unformatted_scan_results_id, repo_path, current_user, scanner_ids_length):
        print("running linguist....")
        linguist_output = os.popen(f"github-linguist {repo_path}").read()
        try:
            unformatted_scan_results_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_results_id)
            unformatted_scan_results_obj['linguist'] = linguist_output
            unformatted_scan_results_obj['updator'] = current_user
            unformatted_scan_results_obj['updated'] = datetime.now(
                timezone.utc)
            unformatted_scan_results_obj.save()
            print("unformatted scan result", unformatted_scan_results_obj)
            unformatted_scan_results_details = json.loads(
                unformatted_scan_results_obj.to_json())
            # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        print("linguist completed")

        # Prepare the prompt for the AI model with specified columns
        prompt = f"""
        Given the following raw GitHub Linguist scan output, convert it into a structured format:
        Raw Scan Output:
        {linguist_output}

        Desired Structured Format:
        [
            {{
                "findings": "",  # Detected languages and their corresponding percentages
                "issue_detail": "",  # Provide details on the issue identified, describing how it was detected, any error messages returned, or other evidence of the vulnerability
                "issue_background": "",  # Explain the technical background and implications of the issue, including common causes and possible attack scenarios, similar to SQL injection example
                "issue_remediation": "",  # Recommend effective steps to fix or mitigate the issue, including best practices and specific configuration or coding practices to avoid it
                "references": "",  # List relevant resources, such as security articles, cheat sheets, or tool documentation, to guide on further investigation or mitigation
                "vulnerability_classifications": "",  # Provide vulnerability classification codes, like CWE or CAPEC, that relate to the issue for easy reference
                "target": "{repo_path}",  # The repository path or name being scanned
                "status": "Open",  # Set to "Open" as a default status
                "risk_level": "low",  # Linguist is mainly informational, so default risk is "low"
                "severity_range": 0,  # A single integer between 1 and 100 representing severity
                "source_scanners": "Linguist",  # Fixed to "Linguist" as the source scanner
                "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # Date of the scan
                "additional_info": ""  # Any extra information, such as special files or configuration notes
            }},
            ...
        ]

        Please ensure:
        - "findings" include the language names and their percentages from the Linguist scan.
        - "risk_level" is set to "low" by default, as Linguist's output is typically informational.
        - Return the result **strictly as a raw JSON array without any additional text or formatting**.
        """


        # Call the OpenAI API to get the structured output
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                         messages=[
                                                             {"role": "user", "content": prompt}],
                                                         temperature=0.7)

        print("response", response)

        structured_results = response.choices[0].message.content
        print("structured_results", structured_results)
        cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        # Ensure the cleaned results are valid JSON
        try:
            json_data = json.loads(cleaned_results)
            print("json_data",json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")

        for result in json_data:
            print("result", result)
            print("result", type(result))
            print("finding",result.get('findings', ''))
            try:
                new_refined_scan_obj = Refined_scan_results(
                    refined_scan_results_id=str(uuid.uuid4()),  # Generate a new unique ID for each record
                    unformatted_scan_results_id=unformatted_scan_results_id,  # Reference the unformatted scan
                    finding=result.get('findings', ''),  # Extract the 'findings' from the result
                    issue_detail=result.get('issue_detail', ''),  
                    issue_background=result.get('issue_background', ''),  
                    issue_remediation=result.get('issue_remediation', ''),  
                    references=result.get('references', ''),  
                    vulnerability_classifications=result.get('vulnerability_classifications', ''), 
                    target=result.get('target', ''),  # Extract the 'target' from the result
                    severity=result.get('risk_level', ''),  # Extract the 'risk_level' as severity
                    severity_range=result.get('severity_range', ''), # Extract the 'severity_range' from the result
                    scan_status=result.get('status', ''), # Extract the 'status' from the result as scan_status
                    scanner=result.get('source_scanners', 'ZAP'),  # Use 'ZAP' as the scanner
                    scan_date=result.get('scan_date', ''),  # Extract the 'scan_date'
                    additional_info=result.get('additional_info', ''),  # Extract 'additional_info'
                    created=datetime.now(timezone.utc),  # Set the creation date to current time
                    creator=current_user  # Set the user creating this entry
                )
                
                new_refined_scan_obj.save()  # Save the record into the database
                print("response", json.loads(new_refined_scan_obj.to_json()))
                # print(f"Saved refined scan result: {new_refined_scan_obj}")

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)

    def run_zap(self, unformatted_scan_results_id, domain, repo_path, current_user, scanner_ids_length):
        print("Running ZAP scan...")

        # Call the new ZAP scan logic from zap_scanner.py
        transformed_alerts = run_zap_scan(domain)

        # Process and store the results (this part remains the same)
        for result in transformed_alerts:
            try:
                new_refined_scan_obj = Refined_scan_results(
                    refined_scan_results_id=str(uuid.uuid4()),
                    unformatted_scan_results_id=unformatted_scan_results_id,
                    finding=result.get('findings', ''),
                    issue_detail=result.get('issue_detail', ''),
                    issue_background=result.get('issue_background', ''),
                    issue_remediation=result.get('issue_remediation', ''),
                    references=result.get('references', ''),
                    vulnerability_classifications=result.get('vulnerability_classifications', ''),
                    target=result.get('target', ''),
                    severity=result.get('risk_level', ''),
                    severity_range=result.get('severity_range', ''),
                    scan_status=result.get('status', ''),
                    scanner=result.get('source_scanners', 'ZAP'),
                    scan_date=result.get('scan_date', ''),
                    additional_info=result.get('additional_info', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_refined_scan_obj.save()
                # print("response", json.loads(new_refined_scan_obj.to_json()))
                new_refined_scan_data = json.loads(new_refined_scan_obj.to_json())
                for instance in result.get('instances', ''): 
                    new_zap_scan_obj = ZapExtendedOutputs(
                        zap_extended_outputs_id=str(uuid.uuid4()),
                        refined_scan_results_id=new_refined_scan_data.get("_id"),
                        uri=instance.get('uri', ''),
                        method=instance.get('method', ''),
                        param=instance.get('param', ''),
                        attack=instance.get('attack', ''),
                        evidence=instance.get('evidence', ''),
                        otherinfo=instance.get('otherinfo', ''),
                        created=datetime.now(timezone.utc),
                        creator=current_user
                    )
                    new_zap_scan_obj.save()
                    # print("response", json.loads(new_zap_scan_obj.to_json()))



            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)

    def run_gitleaks(self, project_id, scan_id, scanner_id, scan_type_id, target_id, repo_path, current_user, scanner_ids_length):
        print("running gitleaks....")
        print(scan_id, project_id, scanner_id, scan_type_id, target_id, repo_path, current_user)

        # Run the Gitleaks scan and capture the output
        try:
            gitleaks_command = f"gitleaks git {repo_path} --verbose --report-format json"
            gitleaks_output = os.popen(gitleaks_command).read()
        except Exception as e:
            print(f"Error running Gitleaks: {e}")
            return {'error': 'Gitleaks execution failed', 'details': e.stderr}

        # Store raw Gitleaks scan output
        try:
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=scanner_id,
                output=gitleaks_output,
                created=datetime.now(timezone.utc),
                creator=current_user
            )
            raw_scan_output_obj.save()
            print("Raw scan output saved:", raw_scan_output_obj)
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        print("completed gitleaks")

        # Prepare the prompt for the AI model with specified columns
        prompt = f"""
        Given the following raw Gitleaks scan output, convert it into a structured format:
        Raw Scan Output:
        {gitleaks_output}

        Desired Structured Format:
        {
            "finding_name": "",  # Speacific leak name, keep it below 5 words
            "finding_desc": "",  # Provide description of the secret leak 
            "status": "open",  # Leaks are marked "open" by default
            "severity": "",  # Risk level (high, medium, low, critical) based on Gitleaks output
            "severity_range": 0,  # A single integer between 1 and 100 representing severity
            "extra" : [{
                "cweid": "", # CWE ID representing the vulnerability classification
                "wascid": "", # WASC ID representing the vulnerability classification
                "secret": "", # The detected secret
                "file_name": "", # File name of the secret detected
                "line_number": "", # The line numbers the secret detected
                "column_number": "", # The column numbers the secret detected
                "fix_time": "", # Time will take to fix this
                "references": "", # List of references related to the vulnerability, e.g., CVE, articles
            }]
        }

        Ensure that the information provided is precise, complete, and highly useful for developers and security teams. 
        Return the result **strictly as a raw JSON Array without any additional text or formatting**.
        """

        # Call the OpenAI API to get the structured output
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                        messages=[
                                                            {"role": "user", "content": prompt}],
                                                        temperature=0.7)

        print("response", response)

        structured_results = response.choices[0].message.content
        print("structured_results", structured_results)

        cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        # Ensure the cleaned results are valid JSON
        try:
            json_data = json.loads(cleaned_results)
            print("json_data", json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {'error': 'Failed to parse JSON from OpenAI response', 'details': str(e)}

        # Iterate through each finding in the structured results and save to the database
        for result in json_data:
            try:
                findings_obj = FindingMaster(
                    finding_id=str(uuid.uuid4()),
                    project_id=project_id,
                    finding_date=datetime.now(timezone.utc),
                    target_id=result.get('target', ''),
                    scan_type_id=scan_type_id,
                    finding_name=result.get('finding_name', ''),
                    finding_desc=result.get('finding_desc', ''),
                    severity=result.get('severity', 'low'),
                    status=result.get('status', 'open'),
                    raw_scan_output_id=raw_scan_output_obj.raw_scan_output_id,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                findings_obj.save()

                # Save detailed findings
                for detail in result.get('extra', []):
                    repo_secret_detections_obj = RepoSecretDetections(
                        repo_secret_detections_id=str(uuid.uuid4()),
                        finding_id=findings_obj.finding_id,
                        secret=result.get('secret', ''),
                        cweid=detail.get('cweid', ''),
                        wascid=detail.get('wascid', ''),
                        file_name=detail.get('file_name', ''),
                        line_number=detail.get('line_number', ''),
                        column_number=detail.get('column_number', ''),
                        fix_time=detail.get('fix_time', ''),
                        references=detail.get('references', []),
                        created=datetime.now(timezone.utc),
                        creator=current_user
                    )
                    repo_secret_detections_obj.save()

            except Exception as e:
                print(f"Unexpected error occurred while saving: {e}")

        # Update scan status
        self.increment_scan_status(raw_scan_output_obj.raw_scan_output_id, scanner_ids_length)
        return "Gitleaks scan completed and results saved.", "200 OK"

    def run_licenses_and_sbom_scan(self, scan_id, scanner_id, scan_type_id, target_id, repo_path, current_user, scanner_ids_length):
        """
        Runs the license and SBOM scan.

        Args:
            scan_id (str): UUID of the scan (collection - scans)
            scanner_id (str): UUID of the scanner (collection - scanners).
            scan_type_id (str): UUID of the scan type (collection - scan_types).
            target_id (str): UUID of the target to scan (collection - target_repository).
            repo_path (str): Path to the repository being scanned.
            current_user (str): User initiating the scan.
        """

        # Store raw Trivy scan output
        raw_scan_output_id=str(uuid.uuid4()),

        # trivy_output = trivyScanner.run_licenses_and_sbom_scan(scan_id, repo_path)

        try:
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=raw_scan_output_id,
                scan_id=scan_id,
                scanner_id=scanner_id,
                output=trivy_output,
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            raw_scan_output_obj.save()
            raw_scan_output_details = json.loads(
                raw_scan_output_obj.to_json())
            print("raw scan result", raw_scan_output_details)
            # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        data = json.loads(trivy_output)
        for result in data["Results"]:
            for pkg in result.get("Packages", []):
                try:
                    license_data = FindingLicensesAndSbom(
                        finding_licenses_and_sbom_id=str(uuid.uuid4()),
                        raw_scan_output_id=raw_scan_output_id,
                        scan_type_id=scan_type_id,
                        target_id=target_id,
                        finding_date=datetime.now(timezone.utc),
                        package_name=pkg.get("Name",""),
                        package_type=result.get("Type",""),
                        package_version=pkg.get("Version",""),
                        license_type=pkg.get("Licenses",[]),
                        relationship=pkg.get("Relationship", ""),
                        created=datetime.now(timezone.utc),
                        creator=current_user,
                    )
                    license_data.save()
                except Exception as e:
                    print("\n Error on saving: ", e)

            for vuln in result.get("Vulnerabilities", []):
                try:
                    license_and_sbom_object = FindingLicensesAndSbom.objects.get(
                        raw_scan_output_id=raw_scan_output_id,
                        scan_type_id=scan_type_id,
                        target_id=target_id,
                        package_name=vuln.get("PkgName", ""),
                        package_version=vuln.get("InstalledVersion", ""),
                        package_type=result.get("Type",""),
                    )
                    license_and_sbom_object['published_date'] = datetime.strptime(vuln["PublishedDate"], "%Y-%m-%dT%H:%M:%S.%fZ") if vuln["PublishedDate"] else None
                    license_and_sbom_object['risk_title'] = vuln.get("Title",None)
                    license_and_sbom_object['risk_desc'] = vuln.get("Description",None)
                    license_and_sbom_object['risk_level'] = vuln["Severity"].lower() if vuln["Severity"] else None
                    license_and_sbom_object['risk_fixed_version'] = vuln.get("FixedVersion",None)
                    license_and_sbom_object['risk_fixed_version'] = vuln.get("References",None)
                    license_and_sbom_object['updator'] = current_user
                    license_and_sbom_object['updated'] = datetime.now(timezone.utc)
                    license_and_sbom_object.save()
                except Exception as e:
                    print("Error on saving: ", e)
        # Update scan status
        self.increment_scan_status(raw_scan_output_id, scanner_ids_length)

    def run_trivy(self, unformatted_scan_results_id, repo_path, current_user, scanner_ids_length):
        """
        Call def run_licenses_and_sbom_scan from services to run trivy scan for licenses and SBOM
        """
        # def install_dependencies(repo_path):
        #     installed = False
        #     for root, _, files in os.walk(repo_path):
        #         # Detecting npm, pip, go.mod, etc.
        #         if 'tests' in root.lower() or 'test' in root.lower():
        #             print(f"Skipping installation in the 'tests' folder: {repo_path}")
        #             continue
        #         if "package.json" in files:
        #             print(f"Detected npm at {root}. Running 'npm install'...")
        #             subprocess.run(["npm", "install"], cwd=root, check=True)
        #             installed = True
        #         elif "requirements.txt" in files:
        #             print(f"Detected pip at {root}. Running 'pip3 install -r requirements.txt'...")
        #             # subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=root, check=True)
        #             # subprocess.run(['pip3', 'install', '--user', '-r', 'requirements.txt'], cwd=repo_path, check=True)
        #             installed = True
        #         elif "go.mod" in files:
        #             print(f"Detected Go at {root}. Running 'go mod tidy'...")
        #             subprocess.run(["go", "mod", "tidy"], cwd=root, check=True)
        #             installed = True
        #         # elif "pom.xml" in files:
        #         #     print(f"Detected Maven at {root}. Running 'mvn install'...")
        #         #     subprocess.run(["mvn", "install"], cwd=root, check=True)
        #         #     installed = True
        #     return installed

        # install_dependencies(repo_path)
        # print("running trivy....")
        # print("repo_path", repo_path)

        # # Run the Trivy scan and capture the output
        # trivy_output = os.popen(f"trivy repo --scanners vuln,secret,misconfig --list-all-pkgs --format json {repo_path}").read()

        # # Store raw Trivy scan output
        # try:
        #     unformatted_scan_results_obj = Unformatted_scan_results.objects.get(
        #         unformatted_scan_results_id=unformatted_scan_results_id)
        #     unformatted_scan_results_obj['trivy'] = trivy_output
        #     unformatted_scan_results_obj['updator'] = current_user
        #     unformatted_scan_results_obj['updated'] = datetime.now(
        #         timezone.utc)
        #     unformatted_scan_results_obj.save()
        #     print("unformatted scan result", unformatted_scan_results_obj)
        #     unformatted_scan_results_details = json.loads(
        #         unformatted_scan_results_obj.to_json())
        #     # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        # except DoesNotExist as e:
        #     return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        # except ValidationError as e:
        #     return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        # print("completed trivy")

        # try:
        #     data = json.loads(trivy_output)
        #     for result in data["Results"]:
        #         # Save Licenses
        #         for pkg in result.get("Packages", []):
        #             license_data = Repo_licenses(
        #                 repo_licenses_id=str(uuid.uuid4()),
        #                 unformatted_scan_results_id=unformatted_scan_results_id,
        #                 package_id=pkg["ID"],
        #                 package_name=pkg["Name"],
        #                 target=result["Target"],
        #                 license=pkg.get("Licenses",[]),
        #                 version=pkg["Version"],
        #                 identifier=pkg.get("Identifier", []),
        #                 dependents=pkg.get("DependsOn", []),
        #                 relationships=pkg["Relationship"],
        #                 locations=pkg.get("Locations", []),
        #                 layer=pkg.get("Layer", []),
        #                 created =datetime.utcnow(),
        #             )
        #             license_data.save()
        #         print("\n -----------------------------------------done packages---------------------------------------")

        #         # Save Vulnerabilities (SBOM)
        #         for vuln in result.get("Vulnerabilities", []):
        #             published_date = datetime.strptime(vuln["PublishedDate"], "%Y-%m-%dT%H:%M:%S.%fZ") if vuln["PublishedDate"] else None
        #             last_modified_date = datetime.strptime(vuln["LastModifiedDate"], "%Y-%m-%dT%H:%M:%S.%fZ") if vuln["LastModifiedDate"] else None
        #             vulnerability_data = Repo_vulnerabilities(
        #                 repo_vulnerabilities_id=str(uuid.uuid4()),
        #                 unformatted_scan_results_id=unformatted_scan_results_id,
        #                 vulnerability= vuln["VulnerabilityID"],
        #                 package_id=vuln.get("PkgID", None),
        #                 package_name=vuln["PkgName"],
        #                 target=result["Target"],
        #                 installed_version = vuln["InstalledVersion"],
        #                 fixed_version =  vuln["FixedVersion"],
        #                 status= vuln["Status"],
        #                 severity= vuln["Severity"],
        #                 severity_source = vuln["SeveritySource"],
        #                 primary_url = vuln["PrimaryURL"],
        #                 title = vuln["Title"],
        #                 description = vuln["Description"],
        #                 references = vuln.get("References",[]),
        #                 published_date = published_date,
        #                 last_modified_date = last_modified_date,
        #                 cvss = json.loads(json.dumps(vuln.get("CVSS", {}))),
        #                 cwe_ids = vuln.get("CweIDs",[]),
        #                 vendor_severity = json.loads(json.dumps(vuln.get("VendorSeverity", {}))),
        #                 layer = json.loads(json.dumps(vuln.get("Layer", {}))),
        #                 created = datetime.utcnow(),
        #             )
        #             vulnerability_data.save()
        #     print("\n -----------------------------------------done storing results-------------------------------------------")
        # except Exception as e:
        #     print("errorroror", e)
        #     print(f"Unexpected error occurred while saving: {e}")
        
        # print("Done Saving Scanned Results............")
        # Prepare the structured prompt for the AI model
        # prompt = f"""
        # Given the following raw Trivy scan output, convert it into a structured format:
        # Raw Scan Output:
        # {trivy_output}

        # Desired Structured Format:
        # [
        #     {{
        #         "findings": "",  # Specific vulnerabilities or issues found in the scan, such as CVEs or misconfigurations
        #         "issue_detail": "",  # Provide details on the issue identified, describing how it was detected, any error messages returned, or other evidence of the vulnerability
        #         "issue_background": "",  # Explain the technical background and implications of the issue, including common causes and possible attack scenarios, similar to SQL injection example
        #         "issue_remediation": "",  # Recommend effective steps to fix or mitigate the issue, including best practices and specific configuration or coding practices to avoid it
        #         "references": "",  # List relevant resources, such as security articles, cheat sheets, or tool documentation, to guide on further investigation or mitigation
        #         "vulnerability_classifications": "",  # Provide vulnerability classification codes, like CWE or CAPEC, that relate to the issue for easy reference
        #         "target": "{repo_path}",  # The target repository, image, or infrastructure component being scanned
        #         "status": "Open",  # Vulnerabilities are "Open" by default
        #         "risk_level": "",  # Risk level based on Trivy output (high, medium, low, critical)
        #         "severity_range": 0,  # A single integer between 1 and 100 representing severity
        #         "source_scanners": "Trivy",  # Fixed to Trivy as the source scanner
        #         "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # Date of the scan in YYYY-MM-DD format
        #         "additional_info": ""  # Extra relevant details, such as package names, versions, or remediation guidance
        #     }},
        #     ...
        # ]

        # Please return the structured data in JSON format.
        # """


        # # Call the OpenAI API to get structured output
        # response = client.chat.completions.create(model="gpt-4o-mini",
        #                                                  messages=[
        #                                                      {"role": "user", "content": prompt}],
        #                                                  temperature=0.7)

        # structured_results = response.choices[0].message.content
        # print("structured_results", structured_results)

        # cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        # # Ensure the cleaned results are valid JSON
        # try:
        #     json_data = json.loads(cleaned_results)
        #     print("json_data",json_data)
        # except json.JSONDecodeError as e:
        #     print(f"Error parsing JSON: {e}")
        # # After obtaining the structured_results from the OpenAI response


        # # Iterate through each finding in the structured results and save to the database
        # for result in json_data:
        #     print("result", result)
        #     print("result", type(result))
        #     print("finding",result.get('findings', ''))
        #     print("target",result.get('target', ''))
        #     print("risk_level",result.get('risk_level', ''))
        #     print("source_scanners",result.get('source_scanners', ''))
        #     print("scan_date",result.get('scan_date', ''))
        #     print("additional_info",result.get('additional_info', ''))
        #     additional_info_value = result.get('additional_info', '')
        #     if not isinstance(additional_info_value, str):
        #         additional_info_value = str(additional_info_value)
        #     try:
        #         new_refined_scan_obj = Refined_scan_results(
        #             refined_scan_results_id=str(uuid.uuid4()),  # Generate a new unique ID for each record
        #             unformatted_scan_results_id=unformatted_scan_results_id,  # Reference the unformatted scan
        #             finding=result.get('findings', ''),  # Extract the 'findings' from the result
        #             issue_detail=result.get('issue_detail', ''),  
        #             issue_background=result.get('issue_background', ''),  
        #             issue_remediation=result.get('issue_remediation', ''),  
        #             references=result.get('references', ''),  
        #             vulnerability_classifications=result.get('vulnerability_classifications', ''), 
        #             target=result.get('target', ''),  # Extract the 'target' from the result
        #             severity=result.get('risk_level', ''),  # Extract the 'risk_level' as severity
        #             severity_range=result.get('severity_range', ''), # Extract the 'severity_range' from the result
        #             scan_status=result.get('status', ''), # Extract the 'status' from the result as scan_status
        #             scanner=result.get('source_scanners', ''),  # Use 'ZAP' as the scanner
        #             scan_date=result.get('scan_date', ''),  # Extract the 'scan_date'
        #             additional_info=additional_info_value,  # Extract 'additional_info'
        #             created=datetime.now(timezone.utc),  # Set the creation date to current time
        #             creator=current_user  # Set the user creating this entry
        #         )
                
        #         new_refined_scan_obj.save()  # Save the record into the database
        #         print("response", json.loads(new_refined_scan_obj.to_json()))
        #         # print(f"Saved refined scan result: {new_refined_scan_obj}")
        #     except Exception as e:
        #         print("errorroror", e)
        #         print(f"Unexpected error occurred while saving: {e}")
        #     # except DoesNotExist as e:
        #     #     print("error",e)
        #     #     return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        #     # except ValidationError as e:
        #     #     print("verror",e)
        #     #     return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        # Update scan status
        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)

    def run_doggo(self, unformatted_scan_results_id, domain, current_user, scanner_ids_length):
        print("running doggo....")

        # Run the Doggo scan and capture the output
        doggo_output = os.popen(f"doggo {domain}").read()
        print("doggo_output", doggo_output)
        # Store raw Doggo scan output
        try:
            unformatted_scan_results_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_results_id)
            unformatted_scan_results_obj['doggo'] = doggo_output
            unformatted_scan_results_obj['updator'] = current_user
            unformatted_scan_results_obj['updated'] = datetime.now(
                timezone.utc)
            unformatted_scan_results_obj.save()
            print("unformatted scan result", unformatted_scan_results_obj)
            unformatted_scan_results_details = json.loads(
                unformatted_scan_results_obj.to_json())
            # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        print("completed doggo")

        # Prepare the structured prompt for the AI model
        # Prepare the structured prompt for the AI model
        prompt = f"""
        Given the following raw Doggo DNS scan output, analyze it and extract the relevant details for each entry.
        Fill in the 'findings' with any noteworthy observations, 'risk_level' based on the presence of any security issues (use 'low' for basic DNS resolution, 'medium' for potential misconfigurations, and 'high' for any critical vulnerabilities like DNS spoofing or poisoning risks), and include any additional context or insights in the 'additional_info' field.

        Raw Scan Output:
        {doggo_output}

        Desired Structured Format:
        [
            {{
                "findings": "<Describe any vulnerabilities, issues, or notable points based on the DNS scan>",
                "issue_detail": "",  # Provide details on the issue identified, describing how it was detected, any error messages returned, or other evidence of the vulnerability
                "issue_background": "",  # Explain the technical background and implications of the issue, including common causes and possible attack scenarios, similar to SQL injection example
                "issue_remediation": "",  # Recommend effective steps to fix or mitigate the issue, including best practices and specific configuration or coding practices to avoid it
                "references": "",  # List relevant resources, such as security articles, cheat sheets, or tool documentation, to guide on further investigation or mitigation
                "vulnerability_classifications": "",  # Provide vulnerability classification codes, like CWE or CAPEC, that relate to the issue for easy reference
                "target": "{domain}",  # The target domain being scanned
                "status": "Open",  # Vulnerabilities are "Open" by default
                "risk_level": "<high/medium/low/critical>",  # Risk level based on Doggo DNS output
                "severity_range": 0,  # A single integer between 1 and 100 representing severity
                "source_scanners": "Doggo",  # Fixed to Doggo DNS for this case
                "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # Date of the scan
                "additional_info": "<Any extra details, like TTLs, specific IPs of interest, or nameservers>"
            }},
            ...
        ]

        Please ensure that every field is filled based on the DNS scan.

        Return the result **strictly as a raw JSON array without any additional text or formatting**.
        """


        # Call the OpenAI API to get structured output
        response = client.chat.completions.create(model="gpt-4o-mini",
                                                         messages=[
                                                             {"role": "user", "content": prompt}],
                                                         temperature=0.7)

        structured_results = response.choices[0].message.content
        print("structured_results", structured_results)

        cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        # Ensure the cleaned results are valid JSON
        try:
            json_data = json.loads(cleaned_results)
            print("json_data",json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        # After obtaining the structured_results from the OpenAI response


        # Iterate through each finding in the structured results and save to the database
        for result in json_data:
            print("result", result)
            print("result", type(result))
            print("finding",result.get('findings', ''))
            print("target",result.get('target', ''))
            print("risk_level",result.get('risk_level', ''))
            print("source_scanners",result.get('source_scanners', ''))
            print("scan_date",result.get('scan_date', ''))
            print("additional_info",result.get('additional_info', ''))
            additional_info_value = result.get('additional_info', '')
            if not isinstance(additional_info_value, str):
                additional_info_value = str(additional_info_value)
            try:
                new_refined_scan_obj = Refined_scan_results(
                    refined_scan_results_id=str(uuid.uuid4()),  # Generate a new unique ID for each record
                    unformatted_scan_results_id=unformatted_scan_results_id,  # Reference the unformatted scan
                    finding=result.get('findings', ''),  # Extract the 'findings' from the result
                    issue_detail=result.get('issue_detail', ''),  
                    issue_background=result.get('issue_background', ''),  
                    issue_remediation=result.get('issue_remediation', ''),  
                    references=result.get('references', ''),  
                    vulnerability_classifications=result.get('vulnerability_classifications', ''), 
                    target=result.get('target', ''),  # Extract the 'target' from the result
                    severity=result.get('risk_level', ''),  # Extract the 'risk_level' as severity
                    severity_range=result.get('severity_range', ''), # Extract the 'severity_range' from the result
                    scan_status=result.get('status', ''), # Extract the 'status' from the result as scan_status
                    scanner=result.get('source_scanners', ''),  # Use 'doggo' as the scanner
                    scan_date=result.get('scan_date', ''),  # Extract the 'scan_date'
                    additional_info=additional_info_value,  # Extract 'additional_info'
                    created=datetime.now(timezone.utc),  # Set the creation date to current time
                    creator=current_user  # Set the user creating this entry
                )
                
                new_refined_scan_obj.save()  # Save the record into the database
                print("response", json.loads(new_refined_scan_obj.to_json()))
                # print(f"Saved refined scan result: {new_refined_scan_obj}")
            except Exception as e:
                print("errorroror", e)
                print(f"Unexpected error occurred while saving: {e}")
            # except DoesNotExist as e:
            #     print("error",e)
            #     return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            # except ValidationError as e:
            #     print("verror",e)
            #     return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        # Update scan status
        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)

    def run_nikto(self, unformatted_scan_results_id, domain, current_user, scanner_ids_length):
        print("Running Nikto asynchronously...")
        
        # Updated tuning options for "123456789abcde"
        tuning_options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e"]
        
        outputs = {}

        def run_command(tuning_option):
            try:
                command = [
                    "nikto",
                    "-h", domain,
                    "-Tuning", tuning_option,
                    "-ssl",  # Force SSL
                    "-Plugins", "ALL",  # Use all plugins
                ]
                print(f"Running command: {' '.join(command)}")
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.stderr:
                    print(f"Error for tuning {tuning_option}: {result.stderr}")
                
                outputs[tuning_option] = result.stdout.strip()

                print(f"Completed scan for Tuning {tuning_option}:")
                print(result.stdout.strip())

            except Exception as e:
                print(f"Error during Nikto scan for tuning {tuning_option}: {e}")

        # Using ThreadPoolExecutor for concurrent execution
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(run_command, tuning_option): tuning_option for tuning_option in tuning_options}
            
            for future in concurrent.futures.as_completed(futures):
                tuning_option = futures[future]
                try:
                    future.result()  # This will raise exceptions if the task failed
                except Exception as e:
                    print(f"Error processing tuning {tuning_option}: {e}")

                print(f"Output for tuning {tuning_option}:")
                print(outputs.get(tuning_option, "No output"))

        # Combine and print the final output
        nikto_output = ""
        for tuning_option in tuning_options:
            nikto_output += f"\nNikto Output for Tuning {tuning_option}:\n{outputs.get(tuning_option, 'No output')}\n"

        if not nikto_output.strip():
            print("No output received from Nikto for all tuning options.")
            return

        print("Final Nikto Output:\n", nikto_output)



        try:
            unformatted_scan_results_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_results_id)
            unformatted_scan_results_obj['nikto'] = nikto_output
            unformatted_scan_results_obj['updator'] = current_user
            unformatted_scan_results_obj['updated'] = datetime.now(timezone.utc)
            unformatted_scan_results_obj.save()
            print("unformatted scan result", unformatted_scan_results_obj)
            unformatted_scan_results_details = json.loads(
                unformatted_scan_results_obj.to_json())
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        print("completed nikto")

        # Updated prompt for OpenAI API
        prompt = f"""
        Given the following raw Nikto scan output, convert it into a structured and detailed format:
        Raw Scan Output:
        {nikto_output}

        Desired Structured Format:
        [
            {{
                "findings": "",  # Detailed list of vulnerabilities identified during the scan e.g., cross-site scripting, SQL injection, etc.
                "issue_detail": "",  # Description of the vulnerability, how it manifests, and how it was detected
                "issue_background": "",  # Explanation of the technical background, causes, and implications of the vulnerability
                "issue_remediation": "",  # Clear, step-by-step guidance on resolving the vulnerability and preventing it in the future including best practices and specific configuration or coding practices to avoid it
                "references": "",  # List of helpful articles, documentation, and external links for additional guidance
                "vulnerability_classifications": "",  # Classification codes such as CWE, CAPEC, or OWASP associated with the vulnerability
                "target": "{domain}",  # The target domain scanned
                "status": "Open",  # Default status for all vulnerabilities
                "risk_level": "",  # Risk level (e.g., high, medium, low, critical) based on Nikto's output
                "severity_range": 0,  # A single integer between 1 and 100 representing severity
                "source_scanners": "Nikto",  # Fixed to Nikto as the source scanner
                "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # Date of the scan in YYYY-MM-DD format
                "additional_info": ""  # Additional observations, anomalies, or related details such as descriptions, URLs, or steps for remediation
            }},
            ...
        ]

        Ensure that the information provided is precise, complete, and highly useful for developers and security teams.
        Please return the structured data in JSON format.
        """

        # Call the OpenAI API to get structured output
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        structured_results = response.choices[0].message.content
        cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        try:
            json_data = json.loads(cleaned_results)
            print("json_data", json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")

        # Save structured results into the database
        for result in json_data:
            try:
                additional_info_value = result.get('additional_info', '')
                if not isinstance(additional_info_value, str):
                    additional_info_value = str(additional_info_value)
                references_value = result.get('references', [])
                if isinstance(references_value, list):
                    references_value = ', '.join(references_value)
                
                vulnerability_classifications_value = result.get('vulnerability_classifications', [])
                if isinstance(vulnerability_classifications_value, list):
                    vulnerability_classifications_value = ', '.join(vulnerability_classifications_value)


                new_refined_scan_obj = Refined_scan_results(
                    refined_scan_results_id=str(uuid.uuid4()),
                    unformatted_scan_results_id=unformatted_scan_results_id,
                    finding=result.get('findings', ''),
                    issue_detail=result.get('issue_detail', ''),
                    issue_background=result.get('issue_background', ''),
                    issue_remediation=result.get('issue_remediation', ''),
                    references=references_value,
                    vulnerability_classifications=vulnerability_classifications_value,
                    target=result.get('target', ''),
                    severity=result.get('risk_level', ''),
                    severity_range=result.get('severity_range', ''), # Extract the 'severity_range' from the result
                    scan_status=result.get('status', ''), # Extract the 'status' from the result as scan_status
                    scanner=result.get('source_scanners', ''),
                    scan_date=result.get('scan_date', ''),
                    additional_info=additional_info_value,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_refined_scan_obj.save()
                print("response", json.loads(new_refined_scan_obj.to_json()))
            except Exception as e:
                print(f"Unexpected error occurred while saving: {e}")

        # Update scan status
        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)
        print(f"No output from Nikto for raw_scan_output_id: {unformatted_scan_results_id}")

    def run_wapiti(self, unformatted_scan_results_id, domain, current_user, scanner_ids_length):
        print("Running Wapiti...")
        print("Target URL:", domain)

        # Create a temporary directory for storing the Wapiti output
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, f"{domain.replace('https://', '').replace('/', '_')}_wapiti.json")

        # Run the Wapiti scan
        wapiti_command = f"wapiti -u {domain} --format json -l 2 --flush-session -m all -o {output_file}"
        wapiti_output = os.popen(wapiti_command).read()

        # Check if the JSON file exists
        if not os.path.exists(output_file):
            shutil.rmtree(temp_dir)  # Clean up the temporary directory
            return None, f"Error: Wapiti JSON output file not found. Command output: {wapiti_output}"

        try:
            # Read and parse the JSON file
            with open(output_file, "r") as file:
                wapiti_results = json.load(file)
                print("Parsed Wapiti Results:", wapiti_results)
        except json.JSONDecodeError as e:
            shutil.rmtree(temp_dir)  # Clean up the temporary directory
            print(f"Error decoding JSON from file: {e}")
            return None, f"Error decoding JSON: {e}"
        except Exception as e:
            shutil.rmtree(temp_dir)  # Clean up the temporary directory
            print(f"Error reading Wapiti output file: {e}")
            return None, str(e)

        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

        # Store raw Wapiti scan output
        try:
            unformatted_scan_results_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_results_id
            )
            unformatted_scan_results_obj.wapiti = wapiti_results
            unformatted_scan_results_obj.updator = current_user
            unformatted_scan_results_obj.updated = datetime.now(timezone.utc)
            unformatted_scan_results_obj.save()
            print("Unformatted scan result:", unformatted_scan_results_obj)
        except DoesNotExist as e:
            return {'error': f'Empty query: {e}'}, '404 Not Found'
        except ValidationError as e:
            return {'error': f'Validation error: {e.message}'}, '400 Bad Request'

        print("Completed Wapiti")

        # Prepare the structured prompt for the AI model
        prompt = f"""
        Given the following raw Wapiti scan output, convert it into a structured and detailed format:
        Raw Scan Output:
        {wapiti_output}

        Desired Structured Format:
        [
            {{
                "findings": "<Describe any vulnerabilities, issues, or notable points based on the DNS scan>",
                "issue_detail": "",  # Provide details on the issue identified, including the exact test data used, describing how it was detected, any error messages returned, or other evidence of the vulnerability
                "issue_background": "",  # Explain the technical background and implications of the issue, including common causes and possible attack scenarios, similar to SQL injection example
                "issue_remediation": "",  # Recommend effective steps to fix or mitigate the issue, including best practices and specific configuration or coding practices to avoid it
                "references": "",  # List relevant resources, such as security articles, cheat sheets, or tool documentation, to guide on further investigation or mitigation
                "vulnerability_classifications": "",  # Provide vulnerability classification codes, like CWE or CAPEC, that relate to the issue for easy reference
                "target": "{domain}",  # The target URL scanned
                "status": "Open",  # Default status for all vulnerabilities
                "risk_level": "",  # Risk level (e.g., high, medium, low, critical)
                "severity_range": 0,  # A single integer between 1 and 100 representing severity
                "source_scanners": "Wapiti",  # Fixed to Wapiti as the source scanner
                "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # Date of the scan in YYYY-MM-DD format
                "additional_info": ""  # Additional observations, anomalies, or related details
            }},
            ...
        ]

        Ensure that the information provided is precise, complete, and highly useful for developers and security teams. 
        The `issue_detail` field must include the exact test data used for detecting the issue.
        Please return the structured data in JSON format.
        """

        # Call the OpenAI API to get structured output
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            structured_results = response.choices[0].message.content
            print("Structured Results:", structured_results)

            # Extract JSON from the structured response
            cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

            # Ensure the cleaned results are valid JSON
            json_data = json.loads(cleaned_results)
            print("JSON Data:", json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None, f"Error parsing structured JSON: {e}"
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None, str(e)

        # Save structured results to the database
        for result in json_data:
            try:
                new_refined_scan_obj = Refined_scan_results(
                    refined_scan_results_id=str(uuid.uuid4()),  # Generate a new unique ID
                    unformatted_scan_results_id=unformatted_scan_results_id,  # Reference the unformatted scan
                    finding=result.get('findings', ''),
                    issue_detail=result.get('issue_detail', ''),
                    issue_background=result.get('issue_background', ''),
                    issue_remediation=result.get('issue_remediation', ''),
                    references=result.get('references', ''),
                    vulnerability_classifications=result.get('vulnerability_classifications', ''),
                    target=result.get('target', ''),
                    severity=result.get('risk_level', ''),
                    severity_range=result.get('severity_range', ''),
                    scan_status=result.get('status', ''),
                    scanner=result.get('source_scanners', ''),
                    scan_date=result.get('scan_date', ''),
                    additional_info=result.get('additional_info', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_refined_scan_obj.save()
                print("Saved Refined Scan Result:", json.loads(new_refined_scan_obj.to_json()))
            except Exception as e:
                print(f"Unexpected error occurred while saving: {e}")

        # Update scan status
        self.increment_scan_status(unformatted_scan_results_id, scanner_ids_length)

        return "Wapiti scan completed and results saved.", "200 OK"


    def cleanup_repo(self, raw_scan_output_id, repo_path):
        # Delete the repository path if it exists
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)

        # Fetch the document from the Unformatted_scan_results collection
        unformatted_scan_obj = Unformatted_scan_results.objects.get(unformatted_scan_results_id=raw_scan_output_id)

        # Update the status field and save the document
        unformatted_scan_obj.status = "completed"
        unformatted_scan_obj.save()