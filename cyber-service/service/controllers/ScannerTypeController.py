# try:
#     # runtime import
#     from entities.InterventionEntity import Intervention
# except Exception as e:
#     # testing import
#     from ..entities.InterventionEntity import Intervention
# from controllers.util import *
# from entities.InterventionEntity import Intervention, Params, Methods, Docs, Assignment, InterventionStatus, Transaction
from typing import List
from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from marshmallow import Schema, fields, ValidationError, INCLUDE
from datetime import datetime, timezone
# from controllers.ValidationController import ValidationController
# from controllers.TransactionController import TransactionController
import uuid
import json
import subprocess
from tempfile import mkdtemp
import shutil
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo import MongoClient
import re
from entities.CyberServiceEntity import ScanTargetType, ScannerTypes
from enum import Enum
class ScanTargetType(Enum):
    REPO = 'repo'
    DOMAIN = 'domain'
    CONTAINER = 'container'
    CLOUD = 'cloud'
    WEB3 = 'web3'
    VM = 'vm'


class ScannerTypeController():
    """
    Defines controller methods for the Intervention Entity.
    """

    def __init__(self) -> None:
        pass

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the domain objects from the database.
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        pipeline = [
            {
                "$match": {
                    **fields,
                    "isdeleted": {"$ne": True}  # Exclude soft-deleted records
                }
            }
        ]

        # Execute the aggregation pipeline
        scans_type_list = list(ScannerTypes.objects.aggregate(pipeline))
        response = scans_type_list
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'

    def run_command(self, command, cwd=None):
        try:
            output = subprocess.check_output(
                command, shell=True, text=True, cwd=cwd, stderr=subprocess.STDOUT
            )
            return output
        except subprocess.CalledProcessError as e:
            return f"Error running command: {str(e)}. Output: {e.output}"

    def strip_ansi_codes(self, text):
        ansi_escape = re.compile(r'\x1B\[[0-?9;]*[mK]')
        return ansi_escape.sub('', text)

    def clone_github_repo(self, repo_url):
        temp_dir = tempfile.mkdtemp()
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
    
    def create_job(self, domain, repo_url, user_id):
        job_id = str(uuid.uuid4())
        repo_path, clone_output = self.clone_github_repo(repo_url)

        if not repo_path:
            return None, f"Failed to clone repository: {clone_output}"

        job = {
            "job_id": job_id,
            "domain": domain,
            "repo_url": repo_url,
            "repo_path": repo_path,
            "status": "pending",
            "scans_status": "0/9",
            "created": datetime.now(timezone.utc),
            "creator": user_id,
            "amass": None,
            "nmap": None,
            "whois": None,
            "linguist": None,
            "zap": None,
            "gitleaks": None,
            "doggo": None,
            "nikto": None,
        }
        jobs_collection.insert_one(job)
        return job_id, None


    def run_scan(self, job_id, domain):
        job = jobs_collection.find_one({"job_id": job_id})
        repo_path = job["repo_path"]
        
        
        scan_futures = []
        with ThreadPoolExecutor() as executor:
            scan_futures.append(executor.submit(self.run_amass, job_id, domain))
            scan_futures.append(executor.submit(self.run_nmap, job_id, domain))
            scan_futures.append(executor.submit(self.run_whois, job_id, domain))
            scan_futures.append(executor.submit(self.run_linguist, job_id, repo_path))
            scan_futures.append(executor.submit(self.run_zap, job_id, domain, repo_path))
            scan_futures.append(executor.submit(self.run_gitleaks, job_id, repo_path))
            scan_futures.append(executor.submit(self.run_trivy, job_id, repo_path))
            scan_futures.append(executor.submit(self.run_doggo, job_id, domain))
            scan_futures.append(executor.submit(self.run_nikto, job_id, domain))

            for future in as_completed(scan_futures):
                try:
                    future.result()  
                except Exception as e:
                    print(f"Error in scan: {e}")

        self.cleanup_repo(job_id, repo_path)

        # Update status and add updated time and updator
        jobs_collection.update_one({"job_id": job_id}, {
            "$set": {
                "status": "completed",
                "updated": datetime.now(timezone.utc),
                "updator": get_current_user_from_jwt_token()['id']
            }
        })

    def increment_scan_status(self, job_id):
        job = jobs_collection.find_one({"job_id": job_id})

        current_status = job.get("scans_status", "0/9")
        completed, total = map(int, current_status.split("/"))
        new_status = f"{completed + 1}/{total}"
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"scans_status": new_status}})

    def run_amass(self, job_id, domain):
        amass_output = os.popen(f"amass enum -d {domain}").read()
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"amass": amass_output}})
        self.increment_scan_status(job_id)

    def run_nmap(self, job_id, domain):
        nmap_output = os.popen(f"nmap {domain}").read()
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"nmap": nmap_output}})
        self.increment_scan_status(job_id)

    def run_whois(self, job_id, domain):
        whois_output = os.popen(f"whois {domain}").read()
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"whois": whois_output}})
        self.increment_scan_status(job_id)

    def run_linguist(self, job_id, repo_path):
        linguist_output = os.popen(f"github-linguist {repo_path}").read()
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"linguist": linguist_output}})
        self.increment_scan_status(job_id)

    def run_zap(self, job_id, domain, repo_path):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_report:
            zap_report_file = temp_report.name

        zap_command = f"/Applications/ZAP.app/Contents/Java/zap.sh -cmd -quickurl http://{domain} -quickout {zap_report_file}"
        zap_output = os.popen(zap_command).read()

        # zap_base_url = 'http://localhost:8080'
        # api_key = 'tmfqqgpr89e8o5v1s1qv6pk27d'
        # target = 'https://dev.fuelfwd.io'

        # # Create an instance of ZapScanner
        # scanner = ZapScanner(zap_base_url, api_key, target)

        # # Start the ZAP scanning process
        # scanner.create_session()
        # scan_id = scanner.spider()
        # scanner.wait_for_spider()
        # scanner.active_scan()
        # scanner.wait_for_active_scan()
        # scanner.generate_report()

        zap_report_content = ""
        if os.path.exists(zap_report_file):
            with open(zap_report_file, 'r') as report:
                zap_report_content = report.read()

        jobs_collection.update_one({"job_id": job_id}, {"$set": {"zap": zap_report_content}})
        os.remove(zap_report_file)
        self.increment_scan_status(job_id)

    def run_gitleaks(self, job_id, repo_path):
        gitleaks_output = os.popen(f"gitleaks git {repo_path} --verbose").read()
        jobs_collection.update_one({"job_id": job_id}, {
            "$set": {
                "gitleaks":  gitleaks_output,
            }
        })
        self.increment_scan_status(job_id)

    def run_trivy(self, job_id, repo_path):
        trivy_output = os.popen(f"trivy repo {repo_path}").read()
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"trivy": trivy_output }})
        self.increment_scan_status(job_id)

    def run_doggo(self, job_id, domain):
        doggo_output = os.popen(f"doggo {domain}").read()
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"doggo": doggo_output}})
        self.increment_scan_status(job_id)

    def run_nikto(self, job_id, repo_path):
        if not repo_path:
            print("Repo path is invalid")
            return

        nikto_command = f"nikto -h {repo_path}"
        nikto_output = os.popen(nikto_command).read()

        if nikto_output:
            jobs_collection.update_one({"job_id": job_id}, {
                "$set": {
                    "nikto": nikto_output,
                }
            })
            self.increment_scan_status(job_id)
        else:
            print(f"No output from Nikto for job_id: {job_id}")

    def cleanup_repo(self, job_id, repo_path):
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"status": "completed"}})

    def add_entity(self, request):
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        request_json = request.get_json()

        scan_types = request_json.get("scan_types", [])
        if not scan_types:
            return jsonify({"error": "No scan types provided"}), 400

        created_entities = []
        for scan in scan_types:
            scan_type = scan.get('scan_type', None)
            scanner_ids = scan.get('scanner_ids', None)
            scan_target_type = scan.get('scan_target_type', None)
            cloud_provider = scan.get('cloud_provider', None)  # New field
            description = scan.get('description', None)
            # Validate required fields
            if not scan_type or not scanner_ids or not scan_target_type or not description:
                return jsonify({"error": f"Missing required field for {scan_type}"}), 400

            # Validate scan_target_type against the enum
            if scan_target_type not in [e.value for e in ScanTargetType]:
                return jsonify({"error": f"Invalid scan_target_type: {scan_target_type}"}), 400

            # Additional validation for cloud
            if scan_target_type == "cloud" and not cloud_provider:
                return jsonify({"error": "cloud_provider is required for cloud scan_target_type"}), 400
            print("####################cloud_provider",cloud_provider)
            scanner_type_entity = ScannerTypes(
                scan_type_id=str(uuid.uuid4()),
                scan_type=scan_type,
                scanner_ids=scanner_ids,
                scan_target_type=scan_target_type,
                cloud_provider=cloud_provider,  # Save cloud provider
                description=description,
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            scanner_type_entity.save()
            created_entities.append(json.loads(scanner_type_entity.to_json()))

        return jsonify({"message": "Scanner types created successfully", "data": created_entities}), 201

    def fetch_job_details(self, job_id):
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401
        job_details = jobs_collection.find_one({"job_id": job_id}, {"_id": 0})
        
        if job_details:
            return jsonify(job_details), 200
        return {'error': 'Job not found'}, 404
    
    def update_entity(self, request,scanner_id):
        if not hasattr(request, 'get_json'):
            return jsonify({"error": "Invalid request object"}), 400

        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        request_json = request.get_json()  
        if not scanner_id:
            return jsonify({"error": "scanner_ids is required"}), 400

        scanner_type_entity = ScannerTypes.objects(scan_type_id=scanner_id).first()
        if not scanner_type_entity:
            return jsonify({"error": "Scanner type not found"}), 404

        for field in ["scan_type", "scan_target_type", "description", "scanner_ids"]:
            if request_json.get(field):
                scanner_type_entity[field] = request_json[field]
                scanner_type_entity.updated = datetime.now(timezone.utc)
                scanner_type_entity.updator = current_user
        scanner_type_entity.save()
        return jsonify({"message": "Scanner type updated successfully", "data": json.loads(scanner_type_entity.to_json())}), 200


    
    def delete_entity(self, scanner_ids):
        verify_jwt_in_request()
        try:
            scanner_type_entity = ScannerTypes.objects.get(scan_type_id=scanner_ids)
            print("entity",scanner_type_entity)
            scanner_type_entity.soft_delete()  
            return {'success': 'Scanner type deleted successfully'}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Scanner type not found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        
        
    def get_scan_target_types(self):
        try:
            scan_target_types = ScannerTypes.objects.distinct('scan_target_type')
            return jsonify({"scan_target_types": scan_target_types}), 200
        except Exception as e:
            return jsonify({"error": f"Error fetching scan target types: {str(e)}"}), 500


