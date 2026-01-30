import io
from flask import request, jsonify
from mongoengine import *
from controllers.util import *
import uuid
from datetime import datetime, timezone
import json
from entities.CyberServiceEntity import Contract, Scans, RawScanOutput, RepositoryTrivy1, LanguagesAndFramework, RepoSmartContractSlither1, TargetAzureCloud, CloudCloudSploitAzure1, FindingSBOMVulnerability, FindingLicense
from entities.CyberServiceEntity import FindingMaster, DomainWapiti1, DomainZap1, FixRecommendations, RawScanOutput, ScannerTypes, Scanners, Domain, RepoSecretDetections, Repository, FindingLicensesAndSbom, TargetGoogleCloud, CloudCloudSploitGoogle1
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utility.zap.zap_scanner import run_zap_scan
from .utility.FindScanTypeId import findScanTypeId
import shutil
import tempfile
import subprocess
import time
import base64
import re, os
from openai import OpenAI
from .utility.zap.zap_scanner import run_zap_scan, convert_raw_output
from .utility.trivy.trivy_scanner import run_trivy_scan, convert_trivy_output, run_package_licenses_scan, run_licenses_and_sbom_scan
from .utility.FindDuplicateFindingAndLink import findDuplicateFindingAndLink, findDuplicateFindingAndLinkForLanguages, findDuplicateFindingAndLinkForSmartContract
from .utility.cloudsploit.azure_cloud_scanner import run_azure_cloud_scan, convert_structured_azure_output, map_scan_type_id
from .utility.cloudsploit.google_cloud_scanner import run_google_cloud_scan, convert_structured_google_output
from .utility.slither.slither_scanner import detect_imported_dependencies, install_dependencies, resolve_local_imports, set_solc_version, extract_solidity_version, rename_directories_with_spaces, chunk_data, process_smart_contract_with_gpt
from controllers.RepositoryController import RepositoryProvider
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')

# Set your OpenAI API key
client = OpenAI(api_key=openai_api_key)


class ScansController():
    """
    Defines controller methods for the Scans Entity.
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
            print("run_command_error", e)
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
    
    def list_solidity_files_in_tree(directory):
        """
        Recursively list all `.sol` files in a directory and its subdirectories in a tree structure.
        """
        tree = {}
        for root, _, files in os.walk(directory):
            sol_files = [file for file in files if file.endswith('.sol')]
            if sol_files:
                relative_path = os.path.relpath(root, directory)
                tree[relative_path] = sol_files

        return tree
    
    def get_solidity_files(self, repo_path):
        """
        Get all Solidity files (*.sol) in the cloned repository.
        """
        sol_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".sol"):
                    sol_file_path = os.path.join(root, file)
                    sol_files.append(sol_file_path)

        # Log the Solidity files found
        if sol_files:
            print(f"Found Solidity files:")
            for file in sol_files:
                print(f"- {file}")
        else:
            print("No Solidity files found.")

        return sol_files
    
    def find_contracts_directories(self, repo_path):
        """
        Recursively find all 'contracts' directories within the given repository path.
        """
        contracts_dirs = []
        for root, dirs, files in os.walk(repo_path):
            for dir_name in dirs:
                if dir_name == "contracts":
                    contracts_dirs.append(os.path.join(root, dir_name))
        
        # Log the contracts directories found
        if contracts_dirs:
            print(f"Found 'contracts' directories:")
            for dir_path in contracts_dirs:
                print(f"- {dir_path}")
        else:
            print("No 'contracts' directories found.")

        return contracts_dirs
    
    def get_cloudsploit_scanner_types(self):
        try:
            # Fetch the scanner object where the name is 'Cloudsploit'
            cloudsploit_scanner = Scanners.objects.get(name="Cloudsploit")
            scanner_id = cloudsploit_scanner.id
        except DoesNotExist:
            print("Scanner 'Cloudsploit' not found")
            return None

        # Fetch the related scanner types if the scanner_id exists
        if scanner_id:
            scanner_types = ScannerTypes.objects(scanner_ids=scanner_id)
            scanner_types_data = json.loads(scanner_types.to_json())
            # Collect a list of dictionaries with scanner_type_id and scan_type
            scan_types_list = [{
                'scanner_type_id': str(scanner_type.get('_id')),
                'scan_type': scanner_type.get('scan_type')
            } for scanner_type in scanner_types_data]
            
            return scan_types_list
        else:
            return None
        
    def get_wapiti_scanner_types(self):
        try:
            # Fetch the scanner object where the name is 'Wapiti'
            Wapiti_scanner = Scanners.objects.get(name="Wapiti")
            scanner_id = Wapiti_scanner.id
        except DoesNotExist:
            print("Scanner 'Wapiti' not found")
            return None

        # Fetch the related scanner types if the scanner_id exists
        if scanner_id:
            scanner_types = ScannerTypes.objects(scanner_ids=scanner_id)
            scanner_types_data = json.loads(scanner_types.to_json())
            # Collect a list of dictionaries with scanner_type_id and scan_type
            scan_types_list = [{
                'scanner_type_id': str(scanner_type.get('_id')),
                'scan_type': scanner_type.get('scan_type')
            } for scanner_type in scanner_types_data]
            
            return scan_types_list
        else:
            return None

    def delete_by_project_id(self, project_id):
        # Filter the records that match the project_id
        records_to_delete = FindingLicensesAndSbom.objects(project_id=project_id)
        
        # Delete the filtered records
        if records_to_delete:
            deletion_count = records_to_delete.delete()  # This will return the number of documents deleted
            print(f"Deleted {deletion_count} records with project_id: {project_id}")
        else:
            print(f"No records found with project_id: {project_id}")

    def generate_google_cloud_config(self, google_cloud_data):
        google_cloud_target_id = google_cloud_data[0].get('_id')
        print("Extracted google_cloud_target_id:", google_cloud_target_id)
        # Map the google_cloud_data fields to the required JSON structure
        azure_credentials = {
            "type": google_cloud_data[0]['type'],
            "project_id": google_cloud_data[0]['gcp_project_id'],
            "private_key_id": google_cloud_data[0]['private_key_id'],
            "private_key": google_cloud_data[0]['private_key'],
            "client_email": google_cloud_data[0]['client_email'],
            "client_id": google_cloud_data[0]['client_id'],
            "auth_uri": google_cloud_data[0]['auth_uri'],
            "token_uri": google_cloud_data[0]['token_uri'],
            "auth_provider_x509_cert_url": google_cloud_data[0]['auth_provider_x509_cert_url'],
            "client_x509_cert_url": google_cloud_data[0]['client_x509_cert_url'],
            "universe_domain": google_cloud_data[0]['universe_domain']
        }
        # Create a JSON file in the system temporary directory
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as temp_file:
            json.dump(azure_credentials, temp_file, indent=4)
            temp_file_path = temp_file.name

        print(f"Temporary JSON file created at: {temp_file_path}")

        cloudsploit_base_path = os.getenv('CLOUDSPLOIT_CLONE_PATH')
        # Path to config_example.js
        google_cloudsploit_config_path = os.path.join(cloudsploit_base_path, "config_example.js")


        # Read the content of config_example.js
        with open(google_cloudsploit_config_path, 'r') as file:
            config_content = file.read()

        # Save the original content to restore later
        google_cloudsploit_original_content = config_content   
        
        # Regex to find the azure section and uncomment the 'credential_file' line, then update the value
        google_credential_pattern = re.compile(
            r"(google:\s*{[^}]*?)//\s*credential_file:\s*process\.env\.GOOGLE_APPLICATION_CREDENTIALS\s*\|\|\s*'[^']*'([^}]*})", 
            re.DOTALL
        )

        # Replace the commented credential_file with the new path and uncomment it
        updated_content = google_credential_pattern.sub(
            rf"\1credential_file: '{temp_file_path}'\2", config_content
        )

        # Write the updated content back to config_example.js
        with open(google_cloudsploit_config_path, 'w') as file:
            file.write(updated_content)

        print(f"Updated 'credential_file' in {google_cloudsploit_config_path} to: {temp_file_path}")
        return google_cloud_data, google_cloud_target_id, google_cloudsploit_config_path, google_cloudsploit_original_content
    
    def add_entity(self, request):
        domain_url =''
        repo_url =''
        contract_url = ''
        contract_target_id = ''
        repo_target_id = ''
        domain_target_id = ''
        access_token =''
        is_private_repo= None
        repository_provider=''
        azure_cloud_target_id= ''
        google_cloud_target_id= ''
        cloudsploit_config_path= ''
        cloudsploit_original_content = None
        contract_label = None
        google_cloudsploit_config_path = ''
        google_cloudsploit_original_content = None
        print("#requestttt", request)
        scheduler_secret = request.get('scheduler_secret', '')
        if scheduler_secret:
            current_user = "Google Cloud Scheduler"
        else:
            # Fetching user id from jwt token and validate jwt token
            current_user = get_current_user_from_jwt_token()
            if not current_user:
                return jsonify({"error": "Unauthorized"}), 401
        print("current_user", current_user)
        # request_json = request.get_json()
        scheduler_details = request.get('scheduler_response', '')
        scheduler_id = scheduler_details.get('_id', '')
        project_id = scheduler_details.get('project_id')
        status = request.get('scan_status', '')

        scanner_type_ids_list = scheduler_details.get('scanner_type_ids_list', '')
        print("scanner_type_ids_list", scanner_type_ids_list)
        if scanner_type_ids_list:
            try:
                # Convert string to ObjectId if needed
                scanner_types_obj = ScannerTypes.objects(scan_type_id__in=scanner_type_ids_list)
                scanner_types_data = json.loads(scanner_types_obj.to_json())
                print("scanner_types_data", scanner_types_data)
                # return {'success': 'Record Deleted Successfully'}, '200 Ok'
            except Exception as e:
                print("Exception", e)
                return {'error': 'Unexpected error: ' + str(e)}, '500 Internal Server Error'

        if scanner_types_data:
            # Step 1: Extract all scanner_ids from each dictionary
            scanner_ids = []
            for data in scanner_types_data:
                scanner_ids.extend(data['scanner_ids'])

            # Step 2: Create a unique list of scanner_ids
            unique_scanner_ids = list(set(scanner_ids))

            # Step 3: Query the Scanners table for all matching scanner_ids
            # Assuming you're using MongoEngine or a similar ORM
            try:
                matching_scanners_obj = Scanners.objects(scanner_id__in=unique_scanner_ids)
                matching_scanners = json.loads(matching_scanners_obj.to_json())
                print("################",matching_scanners) 
            except Exception as e:
                print(f"An error occurred while querying Scanners: {e}")

        unique_scanner_names_list = list({scanner['name'] for scanner in matching_scanners})
        if project_id:
            try:
                domain_obj = Domain.objects(project_id=project_id)
                domain_data = json.loads(domain_obj.to_json())
                
                print("domain_data:", domain_data)
                # Extract domain_url from the first element in the list
                if domain_data:
                    domain_url = domain_data[0].get('domain_url')
                    domain_target_id = domain_data[0].get('_id')
                    print("Extracted domain_url:", domain_url)
                    print("Extracted domain_target_id:", domain_target_id)

                repo_obj = Repository.objects(project_id=project_id)
                repo_data = json.loads(repo_obj.to_json())
                
                print("repo_data:", repo_data)
                # Extract domain_url from the first element in the list
                if repo_data:
                    repository_provider=repo_data[0].get("repository_provider")
                    repo_url = repo_data[0].get('repository_url')
                    repo_target_id = repo_data[0].get('_id')
                    access_token = repo_data[0].get('access_token')
                    is_private_repo = repo_data[0].get('is_private_repo')
                    print("Extracted repo_url:", repo_url)
                    print("Extracted repo_target_id:", repo_target_id)
                    print("Extracted access_token:", access_token)
                    print("Extracted is_private_repo:", is_private_repo)

                contract_obj = Contract.objects(project_id=project_id)
                contract_data = json.loads(contract_obj.to_json())

                print("contract_data:", contract_data)
                # Extract contract_label from the first element in the list
                if contract_data:
                    contract_label = contract_data[0].get('contract_label')
                    contract_url = contract_data[0].get('contract_url')
                    contract_target_id = contract_data[0].get('_id')
                    print("Extracted contract_label:", contract_label)
                    print("Extracted contract_url:", contract_url)
                    print("Extracted contract_target_id:", contract_target_id)

                azure_cloud_obj = TargetAzureCloud.objects(project_id=project_id)
                azure_cloud_data = json.loads(azure_cloud_obj.to_json())
                
                print("azure_cloud_data:", azure_cloud_data)
                if azure_cloud_data:
                    azure_cloud_target_id = azure_cloud_data[0].get('_id')
                    print("Extracted azure_cloud_target_id:", azure_cloud_target_id)
                    # Map the azure_cloud_data fields to the required JSON structure
                    azure_credentials = {
                        "ApplicationID": azure_cloud_data[0]['application_id'],
                        "KeyValue": azure_cloud_data[0]['client_secret_key'],
                        "DirectoryID": azure_cloud_data[0]['directory_id'],
                        "SubscriptionID": azure_cloud_data[0]['subscription_id']
                    }
                    # Create a JSON file in the system temporary directory
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as temp_file:
                        json.dump(azure_credentials, temp_file, indent=4)
                        temp_file_path = temp_file.name

                    print(f"Temporary JSON file created at: {temp_file_path}")

                    cloudsploit_base_path = os.getenv('CLOUDSPLOIT_CLONE_PATH')
                    # Path to config_example.js
                    cloudsploit_config_path = os.path.join(cloudsploit_base_path, "config_example.js")


                    # Read the content of config_example.js
                    with open(cloudsploit_config_path, 'r') as file:
                        config_content = file.read()

                    # Save the original content to restore later
                    cloudsploit_original_content = config_content   
                    
                    # Regex to find the azure section and uncomment the 'credential_file' line, then update the value
                    azure_credential_pattern = re.compile(
                        r"(azure:\s*{[^}]*?)//\s*credential_file:\s*'[^']*'([^}]*})", re.DOTALL
                    )

                    # Replace the commented credential_file with the new path and uncomment it
                    updated_content = azure_credential_pattern.sub(
                        rf"\1credential_file: '{temp_file_path}'\2", config_content
                    )

                    # Write the updated content back to config_example.js
                    with open(cloudsploit_config_path, 'w') as file:
                        file.write(updated_content)

                    print(f"Updated 'credential_file' in {cloudsploit_config_path} to: {temp_file_path}")

                google_cloud_obj = TargetGoogleCloud.objects(project_id=project_id)
                google_cloud_data = json.loads(google_cloud_obj.to_json())
                if google_cloud_data:
                    google_cloud_data, google_cloud_target_id, google_cloudsploit_config_path, google_cloudsploit_original_content = self.generate_google_cloud_config(google_cloud_data)

            except Exception as e:
                print("Exception:", e)
                return {'error': 'Unexpected error: ' + str(e)}, '500 Internal Server Error'
            
        # Creating the Scans entry
        scans_obj = Scans(
            scan_id=str(uuid.uuid4()),
            scheduler_id=scheduler_id,
            project_id=project_id,
            status=status,
            execution_date=datetime.now(timezone.utc),
            duration=None,
            created=datetime.now(timezone.utc),
            creator=current_user,
        )


        # Save the entity to the database
        scans_obj.save()
        response = json.loads(scans_obj.to_json())
        scan_id = response.get('_id', '')
        # Run the scan asynchronously
        executor = ThreadPoolExecutor()
        executor.submit(self.run_scan, project_id, scan_id, domain_target_id, domain_url, repo_target_id, repo_url, access_token, contract_target_id, contract_label, unique_scanner_names_list, matching_scanners, current_user, is_private_repo, azure_cloud_data, azure_cloud_target_id, cloudsploit_config_path, cloudsploit_original_content, google_cloud_data, google_cloud_target_id, google_cloudsploit_config_path, google_cloudsploit_original_content, repository_provider)
        return jsonify({"message": "Scans created successfully", "data": "response"}), 201

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the scans object from the database.
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        pipeline = [
            {
                "$match": {
                    **fields
                }
            },
            {
                "$project": {
                    "isdeleted": 0
                }
            }
        ]

        # Execute the aggregation pipeline
        scans_list = list(Scans.objects.aggregate(pipeline))
        response = scans_list
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'
    
    def run_scan(self, project_id, scan_id, domain_target_id, domain_url, repo_target_id, repo_url, access_token, contract_target_id, contract_label, unique_scanner_names_list, matching_scanners, current_user, is_private_repo, azure_cloud_data, azure_cloud_target_id, cloudsploit_config_path, cloudsploit_original_content, google_cloud_data, google_cloud_target_id, google_cloudsploit_config_path, google_cloudsploit_original_content, repository_provider):
        print("Inside domain run scan")
        print("project_id", project_id)
        print("scan_id", scan_id)
        print("domain", domain_url)
        print("domain_target_id", domain_target_id)
        print("repo_url", repo_url)
        print("repo_target_id", repo_target_id)
        print("contract_target_id", contract_target_id)
        print("contract_label", contract_label) #TODO: Update with contract_url/contract_label
        print("unique_scanner_names_list", unique_scanner_names_list)
        print("matching_scanners", matching_scanners)
        print("is_private_repo", is_private_repo)
        print("azure_cloud_data", azure_cloud_data)
        print("azure_cloud_target_id", azure_cloud_target_id)
        print("google_cloud_data", google_cloud_data)
        print("google_cloud_target_id", google_cloud_target_id)
        print("repository_provider", repository_provider)
        
        if repo_url: 
            try:
                repo_path, clone_output = self.clone_github_repo(repo_url, access_token, repository_provider)
                if not repo_path:
                    print("clone_output" , clone_output)
                    print("Failed to clone repository")
                    # return None, f"Failed to clone repository: {clone_output}"
            except Exception as e:
                print("Exception:", e)
                # return {'error': 'Unexpected error: ' + str(e)}, '500 Internal Server Error'

        scan_futures = []
        with ThreadPoolExecutor() as executor:
            # Submit scanner tasks based on scanner_names_mapped
            if repo_url:
                if 'Linguist' in unique_scanner_names_list:
                    linguist_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Linguist'), None)
                    scan_futures.append(executor.submit(
                        self.run_linguist, project_id, scan_id, repo_target_id, repo_path, current_user, linguist_id))
                # if 'Slither' in unique_scanner_names_list:
                #     slither_scanner_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Slither'), None)
                #     scan_futures.append(executor.submit(
                #         self.run_slither, project_id, scan_id, repo_target_id, slither_scanner_id, current_user))
                if 'Gitleaks' in unique_scanner_names_list:
                    gitleaks_scanner_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Gitleaks'), None)
                    scan_futures.append(executor.submit(
                        self.run_gitleaks, project_id, scan_id, repo_target_id, repo_path, gitleaks_scanner_id, current_user))
                if 'Trivy' in unique_scanner_names_list:
                    trivy_scanner_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Trivy'), None)
                    scan_futures.append(executor.submit(
                        self.run_trivy_vulnerability, project_id, scan_id, repo_target_id, repo_url, current_user, trivy_scanner_id, access_token, is_private_repo))
                    scan_futures.append(executor.submit(
                        self.run_licenses_sbom_scan, project_id, scan_id, repo_target_id, repo_url, repo_path, current_user, trivy_scanner_id, access_token, is_private_repo))
                    scan_futures.append(executor.submit(
                        self.run_licenses_scan, project_id, scan_id, repo_target_id, repo_url, repo_path, current_user, trivy_scanner_id, access_token, is_private_repo))
            if domain_url:
                if 'Zap' in unique_scanner_names_list:
                    zap_scanner_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Zap'), None)
                    scan_futures.append(executor.submit(
                        self.run_zap, project_id, scan_id, domain_target_id, domain_url, zap_scanner_id, current_user))
                if 'Wapiti' in unique_scanner_names_list:
                    wapiti_scanner_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Wapiti'), None)
                    scan_futures.append(executor.submit(
                        self.run_wapiti, project_id, scan_id, domain_target_id, domain_url, current_user, wapiti_scanner_id))
            if azure_cloud_data:
                if 'Cloudsploit' in unique_scanner_names_list:
                    azure_scanner_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Cloudsploit'), None)
                    scan_futures.append(executor.submit(
                        self.run_cloudsploit, project_id, scan_id, azure_cloud_target_id, azure_cloud_data, azure_scanner_id, current_user, cloudsploit_config_path, cloudsploit_original_content))
            if google_cloud_data:
                if 'Cloudsploit' in unique_scanner_names_list:
                    google_scanner_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Cloudsploit'), None)
                    scan_futures.append(executor.submit(
                        self.run_cloudsploit_for_google, project_id, scan_id, google_cloud_target_id, google_cloud_data, google_scanner_id, current_user, google_cloudsploit_config_path, google_cloudsploit_original_content))
            if contract_label:
                if 'Slither' in unique_scanner_names_list:
                    slither_scanner_id = next((scanner['_id'] for scanner in matching_scanners if scanner['name'] == 'Slither'), None)
                    scan_futures.append(executor.submit(
                        self.run_slither, project_id, scan_id, contract_target_id, slither_scanner_id, current_user))
            # if 'Amass' in scanner_ids:
            #     scan_futures.append(executor.submit(
            #         self.run_amass, raw_scan_output_id, domain, current_user, scanner_ids_length))
            # if 'Nmap' in scanner_ids:
            #     scan_futures.append(executor.submit(
            #         self.run_nmap, raw_scan_output_id, domain, current_user, scanner_ids_length))
            # if 'Whois' in scanner_ids:
            #     scan_futures.append(executor.submit(
            #         self.run_whois, raw_scan_output_id, domain, current_user, scanner_ids_length))
            # if 'Doggo' in scanner_ids:
            #     scan_futures.append(executor.submit(
            #         self.run_doggo, raw_scan_output_id, domain, current_user, scanner_ids_length))
            # if 'Nikto' in scanner_names_mapped:
            #     scan_futures.append(executor.submit(
            #         self.run_nikto, raw_scan_output_id, domain, current_user, scanner_ids_length))

        # Wait for all scanners to complete
        for future in as_completed(scan_futures):
            try:
                result = future.result()
                if isinstance(result, dict) and "error" in result:
                    # If any scan has an error, update the scan status and return the error
                    print(f"Error in scan: {result['error']}")
                    Scans.objects.filter(scan_id=scan_id).update(status='error', updated=datetime.now(timezone.utc))
                    return result, 500  # Return error response here
                print("Task completed with result:", result)
            except Exception as e:
                print(f"Exception in thread execution: {e}")
                Scans.objects.filter(scan_id=scan_id).update(status='error', updated=datetime.now(timezone.utc))
                return {"error": f"Unexpected error in scan: {str(e)}"}, 500

        # Update the scan status to 'completed' after all threads finish
        try:
            Scans.objects.filter(scan_id=scan_id).update(status='completed', updated=datetime.now(timezone.utc))
            print(f"Scan with ID {scan_id} marked as 'Completed'")
        except Exception as e:
            print(f"Error updating scan status: {e}")

        return None
    
    def run_zap(self, project_id, scan_id, target_id, domain, zap_scanner_id, current_user):

        # Call the new ZAP scan logic from zap_scanner.py
        raw_output = run_zap_scan(domain)
        structured_op = convert_raw_output(raw_output)
        print(f"Found {len(structured_op)} alerts.")
        # print("#################structured_op", type(structured_op))
        raw_output_str = json.dumps(raw_output)
        try: 
            new_raw_scan_op_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id= scan_id,
                scanner_id= zap_scanner_id,
                output=raw_output_str,
                created=datetime.now(timezone.utc),
                creator=current_user)
            new_raw_scan_op_obj.save()
            # print("response", json.loads(new_raw_scan_op_obj.to_json()))
            new_raw_scan_op_data = json.loads(new_raw_scan_op_obj.to_json())

        except Exception as e:
            # Catch any other unforeseen exceptions
            print(f"General Exception: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, '500 Internal Server Error'
        # Process and store the results
        for result in structured_op:
            try:
                domain_zap_1_record_details = result.get('domain_zap_1_record')
                input_text = domain_zap_1_record_details.get('alert', '')
                scan_type_id = findScanTypeId(input_text, 'scan_type')
                is_found = findDuplicateFindingAndLink(project_id, target_id, scan_type_id, result.get('finding_name', ''), scan_id, current_user)
                if is_found:
                    continue

                new_domain_zap_1 = DomainZap1(
                    domain_zap_1_id=str(uuid.uuid4()),
                    param= domain_zap_1_record_details.get('param', ''),
                    attack= domain_zap_1_record_details.get('attack', ''),
                    reference= domain_zap_1_record_details.get('reference', ''),
                    confidence= domain_zap_1_record_details.get('confidence', ''),
                    cweid= domain_zap_1_record_details.get('cweid', ''),
                    wascid= domain_zap_1_record_details.get('wascid', ''),
                    evidence= domain_zap_1_record_details.get('evidence', ''),
                    method= domain_zap_1_record_details.get('method', ''),
                    other= domain_zap_1_record_details.get('other', ''),
                    alert= domain_zap_1_record_details.get('alert', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_domain_zap_1.save()
                # print("response", json.loads(new_domain_zap_1.to_json()))
                new_domain_zap_1_data = json.loads(new_domain_zap_1.to_json())
                new_fix_recom_obj = FixRecommendations(
                    fix_recommendation_id=str(uuid.uuid4()),
                    scanner_fix= result.get('fix_recommendation'),
                    ai_fix= None,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_fix_recom_obj.save()
                # print("response", json.loads(new_fix_recom_obj.to_json()))
                new_fix_recom_obj_data = json.loads(new_fix_recom_obj.to_json())
                
                new_finding_master_obj = FindingMaster(
                    finding_id=str(uuid.uuid4()),
                    project_id= project_id,
                    finding_date= datetime.now(timezone.utc),
                    target_id=target_id,
                    target_type = 'domain',
                    scan_type_id= scan_type_id,
                    finding_name= result.get('finding_name', ''),
                    finding_desc= result.get('finding_desc', ''),
                    severity= result.get('severity', ''),
                    status= "open",
                    extended_finding_details_name= result.get('extended_finding_details_name', ''),
                    extended_finding_details_id= new_domain_zap_1_data.get('_id', ''),
                    fix_recommendation_id= new_fix_recom_obj_data.get('_id', ''),
                    raw_scan_output_id= new_raw_scan_op_data.get('_id', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_finding_master_obj.save()
                # print("response", json.loads(new_finding_master_obj.to_json()))
                new_finding_master_data = json.loads(new_finding_master_obj.to_json())

            except Exception as e:
                # Catch any other unforeseen exceptions
                print(f"General Exception: {e}")
                return {'error': f'Unexpected error: {str(e)}'}, '500 Internal Server Error'
        
        return None

    def run_wapiti(self, project_id, scan_id, target_id, domain_url, current_user, wapiti_scanner_id):
        print("Running Wapiti...")
        print("Wapiti Target URL:", domain_url)

        # Create a temporary directory for storing Wapiti output
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(
            temp_dir, f"{domain_url.replace('https://', '').replace('/', '_')}_wapiti.json")
        print("Output file path for Wapiti", output_file)

        # Build the Wapiti command
        wapiti_command = [
            "/usr/local/bin/wapiti",
            "-u", domain_url,
            "--format", "json",
            "-l", "1",
            "--flush-session",
            "-o", output_file
        ]

        try:
            # Run Wapiti command in the background using subprocess.Popen
            print("Running Wapiti command:", wapiti_command)
            process = subprocess.Popen(
                wapiti_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Check if Wapiti is running in the background
            while process.poll() is None:
                print("Wapiti is still running...")
                time.sleep(10)  # Check every 10 seconds

            # After Wapiti finishes, capture the output and error (if any)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                print("Wapiti scan completed successfully.")
                wapiti_output = stdout
            else:
                shutil.rmtree(temp_dir)
                print(f"Error running Wapiti: {stderr}")
                return None, f"Error running Wapiti: {stderr}"

        except FileNotFoundError:
            print("Error: Wapiti is not installed or not found in the system path.")
            shutil.rmtree(temp_dir)
            return None, "Error: Wapiti is not installed or not found in the system path."

        # Check if the output file exists
        if not os.path.exists(output_file):
            print("Error: Wapiti JSON output file not found.")
            shutil.rmtree(temp_dir)
            return None, "Error: Wapiti JSON output file not found."

        try:
            # Parse the JSON file
            with open(output_file, "r") as file:
                wapiti_results = json.load(file)
                print("Parsed Wapiti Results:", wapiti_results)
        except json.JSONDecodeError as e:
            print(f"Wapiti Error decoding JSON: {e}")
            shutil.rmtree(temp_dir)
            return None, f"Error decoding JSON: {e}"
        except Exception as e:
            print(f"Following Exception on Wapiti: {e}")
            shutil.rmtree(temp_dir)
            return None, str(e)

        # Clean up the temporary directory
        shutil.rmtree(temp_dir)
        print("Wapiti temp directory removed.")
        
        # Save raw scan output
        try:
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=wapiti_scanner_id,
                output=wapiti_output,
                created=datetime.now(timezone.utc),
                creator=current_user
            )
            raw_scan_output_obj.save()
            print("Wapiti Raw scan output saved:", raw_scan_output_obj)
            raw_scan_output_data = json.loads(
                raw_scan_output_obj.to_json())
        except Exception as e:
            print(f"Following Exception on saving raw scan output: {e}")
            return {'error': f'Error saving raw output: {e}'}, '500 Internal Server Error'

        # Prepare the OpenAI API prompt
        prompt = f"""
        Given the following raw Wapiti scan output, convert it into a structured and detailed format:
        Raw Scan Output:
        {wapiti_output}

        Desired Structured Format:
        [
            {{
                "findings": "<Describe any vulnerabilities, issues, or notable points based on the Wapiti scan>",
                "issue_detail": "",  # Provide details on the issue identified, including the exact test data used, describing how it was detected, any error messages returned, or other evidence of the vulnerability
                and Truncate this field to a maximum of 255 characters
                "issue_background": "",  # Explain the technical background and implications of the issue, including common causes and possible attack scenarios
                "issue_remediation": "",  # Recommend effective steps to fix or mitigate the issue, including best practices and specific configuration or coding practices to avoid it
                "references": "",  # List relevant resources, such as security articles, cheat sheets, or tool documentation
                "vulnerability_classifications": "",  # Provide vulnerability classification codes, like CWE or CAPEC
                "target": "{domain_url}",  # The target URL scanned
                "status": "open",  # Default status for all vulnerabilities
                "risk_level": "",  # Risk level (e.g., high, medium, low, critical, informational)
                "severity_range": 0,  # A single integer between 1 and 100 representing severity
                "source_scanners": "Wapiti",  # Fixed to Wapiti as the source scanner
                "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",  # Date of the scan in YYYY-MM-DD format
                "additional_info": "",  # Additional observations, anomalies, or related details
                "detailed_findings": [  # This section includes detailed data for the vulnerabilities
                    {{
                        "vulnerability_type": "<Type of vulnerability discovered, e.g., SQL Injection, XSS>",
                        "alert_name": "<Map to the specific vulnerability header (alert name) from Wapiti's predefined vulnerabilities list>",
                        "affected_parameters": ["<parameter1>", "<parameter2>"],  # Ensure this field is always a list of affected parameters
                        "http_method": "<HTTP method used for the request, e.g., GET, POST>",
                        "payload": "<Payload used in the scan for triggering the vulnerability>",
                        "evidence": "<Evidence that the vulnerability exists, e.g., error messages, response body>",
                        "cwe_id": "<CWE ID representing the vulnerability classification, e.g., CWE-79>",
                        "references": "<List of references related to the vulnerability, e.g., CVE, articles>",
                        "http_request": "<Full HTTP request made during the scan triggering the vulnerability>",
                        "curl_command": "<Equivalent curl command to reproduce the vulnerability>",
                        "module": "<Wapiti module that detected the vulnerability, e.g., XSS, SQL Injection>"
                    }},
                    ...
                ]
            }},
            ...
        ]

        Ensure that the information provided is precise, complete, and highly useful for developers and security teams. 
        The `issue_detail` field must include the exact test data used for detecting the issue.
        Ensure the `issue_detail` field is no longer than 255 characters.
        Map `risk_level` to **critical, high, medium, low, informational**.
        Map `status` to Open, Closed, Ignored, or FalsePositive.
        Ensure that the `alert_name` field includes the exact vulnerability header name of Wapiti Scanner (e.g., "SQL Injection", "Cross Site Request Forgery", "HTTP Strict Transport Security (HSTS)", etc.).
        Ensure `affected_parameters` is always a **list**, even if only one parameter is affected.
        Please return the structured data in JSON format.
        """

        # Generate structured findings using OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            structured_results = response.choices[0].message.content
            print("Structured Results from OpenAI:", structured_results)

            # Extract and validate JSON
            cleaned_results = structured_results.split(
                '```json', 1)[-1].strip().rstrip('`')
            findings_data = json.loads(cleaned_results)
        except json.JSONDecodeError as e:
            return None, f"Error parsing structured JSON: {e}"
        except Exception as e:
            return None, str(e)

        # Save findings and details in the database
        try:
            wapiti_scanners_data = self.get_wapiti_scanner_types()

            for result in findings_data:
                # Save detailed findings
                # domain_wapiti_1_record_details = result.get(
                #     'detailed_findings', [])
                # input_text = domain_wapiti_1_record_details[0].get(
                #     'alert_name', '')
                # scan_type_id = findScanTypeId(input_text, 'scan_type')
                scan_type_id = map_scan_type_id(result, wapiti_scanners_data)

                is_found = findDuplicateFindingAndLink(project_id, target_id, scan_type_id, result.get('findings', ''), scan_id, current_user)
                if is_found:
                    continue

                for detail in result.get('detailed_findings', []):
                    wapiti_extended_obj = DomainWapiti1(
                        domain_wapiti_1_id=str(uuid.uuid4()),
                        url=result.get('target', ''),
                        vulnerability_type=detail.get(
                            'vulnerability_type', ''),
                        alert=detail.get('alert_name', ''),
                        affected_parameters=detail.get(
                            'affected_parameters', []),
                        http_method=detail.get('http_method', ''),
                        payload=detail.get('payload', ''),
                        evidence=detail.get('evidence', ''),
                        cwe_id=detail.get('cwe_id', ''),
                        references=detail.get('references', ''),
                        http_request=detail.get('http_request', ''),
                        curl_command=detail.get('curl_command', ''),
                        module=detail.get('module', ''),
                        created=datetime.now(timezone.utc),
                        creator=current_user
                    )
                    wapiti_extended_obj.save()
                    print("Saved DomainWapiti1 Object:", wapiti_extended_obj)
                    new_domain_wapiti_1_data = json.loads(
                        wapiti_extended_obj.to_json())

                new_fix_recom_obj = FixRecommendations(
                    fix_recommendation_id=str(uuid.uuid4()),
                    scanner_fix=result.get('issue_remediation', ''),
                    ai_fix=None,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_fix_recom_obj.save()
                new_fix_recom_obj_data = json.loads(
                    new_fix_recom_obj.to_json())

                # Save the main finding
                findings_obj = FindingMaster(
                    finding_id=str(uuid.uuid4()),
                    project_id=project_id,
                    finding_date=datetime.now(timezone.utc),
                    target_id=target_id,
                    target_type = 'domain',
                    scan_type_id=scan_type_id,
                    finding_name=result.get('findings', ''),
                    finding_desc=result.get('issue_detail', '')[:255],
                    severity=result.get('risk_level', 'low'),
                    status=result.get('status', 'open'),
                    raw_scan_output_id=raw_scan_output_data.get('_id', ''),
                    extended_finding_details_name='DomainWapiti1',
                    extended_finding_details_id=new_domain_wapiti_1_data.get(
                        '_id', ''),
                    fix_recommendation_id=new_fix_recom_obj_data.get(
                        '_id', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                findings_obj.save()
                print("Saved Wapiti Finding Master Object:", findings_obj)

        except Exception as e:
            return None, f"Error saving findings: {e}"

        return "Wapiti scan completed and results saved.", "200 OK"
    
    def run_gitleaks(self, project_id, scan_id, target_id, repo_path, gitleaks_scanner_id, current_user):
        print("Running Gitleaks...")
        print(project_id, scan_id, target_id, repo_path, gitleaks_scanner_id, current_user)

        try:
           # Get the default branch (main or master) from the local repo
            default_branch = self.get_default_branch(repo_path)
            if not default_branch:
                raise Exception("Failed to retrieve the default branch.")

            print(f"Scanning repository on default branch: {default_branch}")

            # Ensure the repository is on the correct default branch
            # Check the current branch
            current_branch = os.popen(f"git -C {repo_path} rev-parse --abbrev-ref HEAD").read().strip()

            if current_branch != default_branch:
                checkout_command = f"git -C {repo_path} checkout {default_branch}"
                os.system(checkout_command)

            # Run Gitleaks on the current state (the most up-to-date branch)
            gitleaks_command = f"gitleaks dir {repo_path} --verbose --report-format json"
            gitleaks_output = os.popen(gitleaks_command).read()

            print("Gitleaks Output:", gitleaks_output)

            # Save the raw Gitleaks output to the database
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=gitleaks_scanner_id,
                output=gitleaks_output,
                created=datetime.now(timezone.utc),
                creator=current_user
            )
            raw_scan_output_obj.save()
            print("Raw scan output saved:", raw_scan_output_obj)

        except Exception as e:
            print(f"Error running Gitleaks: {e}")
            return {'error': 'Gitleaks execution failed', 'details': str(e)}

        print("Completed Gitleaks")

        # Filter and validate results to remove false positives
        validated_results = self.filter_and_validate_results(gitleaks_output, repo_path)
        length_of_validated_results = len(validated_results)
        # Prepare the prompt for the AI model with specified columns
        prompt = f"""
        Given the following validated Raw Gitleaks findings, convert them into a structured format:
        Validated Raw Scan Findings:
        {validated_results}

        Desired Structured Format:
        [
        {{
            "finding_name": "",  # Specific leak name, keep it below 5 words. For example: "Encryption Key leaked"
            "finding_desc": "",  # Provide description of the secret leak
            "status": "open",  # Leaks are marked "open" by default
            "severity": "",  # Risk level (high, medium, low, critical) based on Gitleaks output
            "severity_range": 0,  # A single integer between 1 and 100 representing severity
            "extra" : {{
                "cweid": "",  # CWE ID representing the vulnerability classification
                "wascid": "",  # WASC ID representing the vulnerability classification
                "secret": "",  # The detected secret
                "file_name": "",  # Full path of the file where the secret was detected, including the relative repository path
                "line_number": "",  # Exact line number where the secret was detected
                "column_number": "",  # Exact column number where the secret was detected, if available
                "references": ""  # List of references related to the vulnerability, e.g., CVE, articles
            }}
        }}
        ]

        Ensure that the information provided is precise, complete, and highly useful for developers and security teams. 
        Return the result **strictly as a raw JSON Array without any additional text or formatting**.
        There are {length_of_validated_results} gitleaks output, i expect same number of output in desired structure.
        """

        # Call the OpenAI API to get the structured output
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        print("Response from OpenAI:", response)

        structured_results = response.choices[0].message.content
        print("Structured Results:", structured_results)

        cleaned_results = structured_results.split('```json', 1)[-1].strip().rstrip('`')

        # Ensure the cleaned results are valid JSON
        try:
            json_data = json.loads(cleaned_results)
            print("Validated JSON Data:", json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {'error': 'Failed to parse JSON from OpenAI response', 'details': str(e)}

        input_text = "Secrets Detection"
        scan_type_id = findScanTypeId(input_text, 'scan_type')

        # Save structured findings to the database
        for result in json_data:
            try:
                extra = result.get('extra', [])
                references = extra.get('references', [])
                if not isinstance(references, list):
                    references = [references]

                is_found = findDuplicateFindingAndLink(project_id, target_id, scan_type_id, result.get('finding_name', ''), scan_id, current_user)
                if is_found:
                    continue

                repo_secret_detections_obj = RepoSecretDetections(
                    repo_secret_detections_id=str(uuid.uuid4()),
                    secret=result.get('secret', ''),
                    cweid=extra.get('cweid', ''),
                    wascid=extra.get('wascid', ''),
                    file_name=extra.get('file_name', ''),
                    line_number=extra.get('line_number', ''),
                    column_number=extra.get('column_number', ''),
                    fix_time=extra.get('fix_time', ''),
                    references=references,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                repo_secret_detections_obj.save()
                repo_secret_detections_data = json.loads(repo_secret_detections_obj.to_json())

                new_fix_recom_obj = FixRecommendations(
                    fix_recommendation_id=str(uuid.uuid4()),
                    scanner_fix=None,
                    ai_fix=None,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_fix_recom_obj.save()
                new_fix_recom_obj_data = json.loads(new_fix_recom_obj.to_json())

                findings_obj = FindingMaster(
                    finding_id=str(uuid.uuid4()),
                    project_id=project_id,
                    finding_date=datetime.now(timezone.utc),
                    target_id=target_id,
                    target_type='repo',
                    scan_type_id=scan_type_id,
                    finding_name=result.get('finding_name', ''),
                    finding_desc=result.get('finding_desc', ''),
                    severity=result.get('severity', 'low'),
                    status=result.get('status', 'open'),
                    extended_finding_details_name='RepoSecretDetections',
                    extended_finding_details_id=repo_secret_detections_data.get('_id', ''),
                    raw_scan_output_id=raw_scan_output_obj.raw_scan_output_id,
                    fix_recommendation_id=new_fix_recom_obj_data.get('_id', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                findings_obj.save()
            except Exception as e:
                print(f"Unexpected error occurred while saving: {e}")

        print("Gitleaks scan completed and results saved.")
        return "Gitleaks scan completed and results saved.", "200 OK"

    def get_default_branch(self, repo_path):
        """Fetch the default branch from the local repository."""
        try:
            response = os.popen(f"git -C {repo_path} symbolic-ref refs/remotes/origin/HEAD").read()
            default_branch = response.strip().split('/')[-1]
            return default_branch
        except Exception as e:
            print(f"Error fetching default branch: {e}")
            return ""

    def filter_and_validate_results(self, gitleaks_output, repo_path):
        """
        Filters and validates Gitleaks results by cleaning output,
        validating file existence, and filtering out false positives.
        """
        try:
            # Clean up the Gitleaks output by removing ANSI escape sequences (color codes)
            gitleaks_output_clean = self.strip_ansi_escape_sequences(gitleaks_output)

            # Parse the cleaned Gitleaks output
            validated_results = self.parse_gitleaks_output(gitleaks_output_clean, repo_path)

            # Filter out false positives
            final_results = []
            for finding in validated_results:
                if not self.is_false_positive(finding):
                    final_results.append(finding)

            validated_results = []
            for result in final_results:
                # Remove repo_path from 'File' and 'Fingerprint'
                if 'File' in result:
                    result['File'] = result['File'].replace(repo_path, '')
                if 'Fingerprint' in result:
                    result['Fingerprint'] = result['Fingerprint'].replace(repo_path, '')

                # Add the validated result to the final results list
                validated_results.append(result)
            return validated_results

        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            return []

        except Exception as e:
            print(f"Error filtering Gitleaks results: {e}")
            return []

    def parse_gitleaks_output(self, gitleaks_output, repo_path):
        """
        Parses Gitleaks output to extract findings and validate them based on file names in the repository.
        
        Parameters:
            gitleaks_output (str): Raw output from Gitleaks.
            repo_path (str): Path to the local repository being scanned.

        Returns:
            list: A list of validated findings as dictionaries.
        """
        # Generate findings from Gitleaks output
        def generate_findings(gitleaks_output):
            for finding in gitleaks_output.strip().split("\n\n"):
                yield finding

        findings = generate_findings(gitleaks_output)
        validated_results = []

        # Collect all file names in the repository into a set for quick lookup
        repo_file_names = {file for _, _, files in os.walk(repo_path) for file in files}

        # Process each finding
        for finding in findings:
            finding_dict = self.parse_finding(finding)
            if not finding_dict:
                continue

            # Extract the file name from the finding
            file_name = os.path.basename(finding_dict.get("File", "").strip())

            # Check if the file name exists in the repository
            if file_name not in repo_file_names:
                print(f"Skipping non-existent file name: {file_name}")
                continue

            # Add to validated results
            validated_results.append(finding_dict)

        return validated_results

    def parse_finding(self, finding_text):
        """Parse a single finding text block into a dictionary."""
        finding_dict = {}
        for line in finding_text.split("\n"):
            match = re.match(r"(\w+):\s+(.*)", line)
            if match:
                key, value = match.groups()
                finding_dict[key] = value
        return finding_dict

    def strip_ansi_escape_sequences(self, text):
        """
        Remove ANSI escape sequences (color codes) from the Gitleaks output.
        """
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', text)

    def is_false_positive(self, finding):
        """
        Additional filtering for false positives based on known patterns or rules.
        """
        ignore_patterns = [
            "dummy",        # Ignore files with "dummy" in their path or content
            "test",         # Ignore files in test-related paths
            "example-key",  # Ignore matches with "example-key"
        ]

        # Check the match or path for known false-positive patterns
        for pattern in ignore_patterns:
            if pattern in finding.get("File", "").lower() or pattern in finding.get("Secret", "").lower():
                return True
        return False

    def run_trivy_vulnerability(self, project_id, scan_id, target_id, repo_path, current_user, trivy_scanner_id, access_token, is_private_repo):
        print("running Trivy Vulnerability scan....")
        print(project_id, scan_id, target_id, repo_path, trivy_scanner_id, current_user)
        # Call the new Trivy scan logic from trivy_scanner.py
        trivy_raw_output, trivy_json_data = run_trivy_scan(repo_path, access_token, is_private_repo)
        print("Trivy raw scan completed")
        structured_trivy_output = convert_trivy_output(trivy_json_data)
        print("Trivy output converted to structured format")
        try:
            new_trivy_raw_scan_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=trivy_scanner_id,
                output=trivy_raw_output,
                created=datetime.now(timezone.utc),
                creator=current_user)
            new_trivy_raw_scan_obj.save()
            print("Trivy raw scan output saved")
            new_trivy_raw_scan_data = json.loads(new_trivy_raw_scan_obj.to_json())
        
        except Exception as e:
            print(f"Unexpected error occurred while saving: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, '500 Internal Server Error'
        # Process and store the results
        for result in structured_trivy_output:
            try:
                repo_trivy_1_record_details = result.get('repository_trivy_1_record')

                input_text = "Dependency Vulnerability Scanner"
                scan_type_id = findScanTypeId(input_text, 'scan_type')

                is_found = findDuplicateFindingAndLink(project_id, target_id, scan_type_id, result.get('findings', ''), scan_id, current_user)
                if is_found:
                    continue

                new_repo_trivy_1 = RepositoryTrivy1(
                    repository_trivy_1_id=str(uuid.uuid4()),  # Generate unique ID for the document
                    finding_id=repo_trivy_1_record_details.get('finding_id', ''),
                    alert=repo_trivy_1_record_details.get('alert', ''),
                    uri=repo_trivy_1_record_details.get('uri', ''),
                    param=repo_trivy_1_record_details.get('param', ''),
                    evidence=repo_trivy_1_record_details.get('evidence', ''),
                    otherinfo=repo_trivy_1_record_details.get('otherinfo', ''),
                    cweid=repo_trivy_1_record_details.get('cweid', []),  # If cweid is a list
                    target_host=repo_trivy_1_record_details.get('target_host', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_repo_trivy_1.save()
                new_repo_trivy_1_data = json.loads(new_repo_trivy_1.to_json())
                new_fix_recom_obj = FixRecommendations(
                    fix_recommendation_id=str(uuid.uuid4()),
                    scanner_fix= repo_trivy_1_record_details.get('fixed_version'),
                    ai_fix= None,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_fix_recom_obj.save()
                # print("response", json.loads(new_fix_recom_obj.to_json()))
                new_fix_recom_obj_data = json.loads(new_fix_recom_obj.to_json())

                findings_obj = FindingMaster(
                    finding_id=str(uuid.uuid4()),
                    project_id=project_id,
                    finding_date=datetime.now(timezone.utc),
                    target_id=target_id,
                    target_type = 'repo',
                    scan_type_id=scan_type_id,
                    finding_name=result.get('finding_name', ''),
                    finding_desc=result.get('finding_desc', '')[:255],
                    severity=result.get('severity', ''),
                    status=result.get('status', 'open'),
                    raw_scan_output_id=new_trivy_raw_scan_data.get('_id', ''),
                    extended_finding_details_name='RepositoryTrivy1',
                    extended_finding_details_id=new_repo_trivy_1_data.get(
                        '_id', ''),
                    fix_recommendation_id=new_fix_recom_obj_data.get(
                        '_id', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                findings_obj.save()
                print("Saved Trivy Finding Master Object:", findings_obj)
        
            except Exception as e:
                return None, f"Error saving findings: {e}"

        return "Trivy scan completed and results saved.", "200 OK"

    def run_licenses_sbom_scan(self, project_id, scan_id, target_id, repo_url, repo_path, current_user, trivy_scanner_id, access_token, is_private_repo):
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

        trivy_raw_data, trivy_json_data = run_licenses_and_sbom_scan(repo_path, access_token, is_private_repo)
        trivy_raw_data_str = json.dumps(trivy_raw_data)
        try:
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=trivy_scanner_id,
                output=trivy_raw_data_str,
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            raw_scan_output_obj.save()
            raw_scan_output_details = json.loads(
                raw_scan_output_obj.to_json())
            print("raw scan result", raw_scan_output_details)
            # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except Exception as e:
            print("general exception", e)
            return None, f"Error saving findings: {e}"
        
        self.delete_by_project_id(project_id)

        input_text = "Licenses and SBOM"
        scan_type_id = findScanTypeId(input_text, 'scan_type')
        try:
            for data in trivy_json_data.get("Results", []):
                if "Vulnerabilities" in data:
                    for vulnerability in data["Vulnerabilities"]:
                        new_vulnerability_obj = FindingSBOMVulnerability(
                            sbom_vulnerability_id=str(uuid.uuid4()),
                            project_id=project_id,
                            scan_type_id=scan_type_id,
                            target_id=target_id,
                            target_type="repo",
                            vulnerabilityid=vulnerability["VulnerabilityID"],
                            pkgid=vulnerability["PkgID"],
                            pkg_name=vulnerability["PkgName"],
                            pkg_identifier=vulnerability["PkgIdentifier"],
                            installed_version=vulnerability["InstalledVersion"],
                            fixed_version=vulnerability.get("FixedVersion", ""),
                            status=vulnerability["Status"],
                            severity_source=vulnerability["SeveritySource"],
                            primary_url=vulnerability["PrimaryURL"],
                            data_source=vulnerability["DataSource"],
                            title=vulnerability["Title"],
                            severity=vulnerability["Severity"],
                            description=vulnerability["Description"],
                            # cwe_ids=vulnerability["CweIDs"],
                            vendor_severity=vulnerability["VendorSeverity"],
                            # CVSS=vulnerability["CVSS"],
                            references=json.dumps(vulnerability["References"]),
                            created=datetime.now(timezone.utc),
                            creator=current_user,
                        )
                        new_vulnerability_obj.save()
                        print("Vulnerability saved")
            
                if "Licenses" in data:
                    for license in data["Licenses"]:
                        new_license_obj = FindingLicense(
                            license_id=str(uuid.uuid4()),
                            project_id=project_id,
                            scan_type_id=scan_type_id,
                            target_id=target_id,
                            target_type="repo",
                            severity=license["Severity"],
                            category=license["Category"],
                            pkg_name=license["PkgName"],
                            file_path=license["FilePath"],
                            name=license["Name"],
                            text=license["Text"],
                            # confidence=license["Confidence"],
                            link=license["Link"],
                            created=datetime.now(timezone.utc),
                            creator=current_user,
                        )
                        new_license_obj.save()
                        print("License saved")
        except Exception as e:
            print(f"Unexpected error occurred while saving: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, '500 Internal Server Error'
        print("Trivy scan completed for license.")
        return {"message": "Trivy scan for License and SBOM completed and results saved."}, 200
    
    def run_licenses_scan(self, project_id, scan_id, target_id, repo_url, repo_path, current_user, trivy_scanner_id, access_token, is_private_repo):
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

        trivy_raw_data, trivy_json_data = run_package_licenses_scan(repo_path, access_token, is_private_repo)
        trivy_raw_data_str = json.dumps(trivy_raw_data)
        try:
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=trivy_scanner_id,
                output=trivy_raw_data_str,
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            raw_scan_output_obj.save()
            raw_scan_output_details = json.loads(
                raw_scan_output_obj.to_json())
            print("raw scan result", raw_scan_output_details)
            # return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except Exception as e:
            print("general exception", e)
            return None, f"Error saving findings: {e}"
        
        self.delete_by_project_id(project_id)

        input_text = "Licenses and SBOM"
        scan_type_id = findScanTypeId(input_text, 'scan_type')
        try:
            for data in trivy_json_data.get("Results", []):
                if "Vulnerabilities" in data:
                    for vulnerability in data["Vulnerabilities"]:
                        new_vulnerability_obj = FindingSBOMVulnerability(
                            sbom_vulnerability_id=str(uuid.uuid4()),
                            project_id=project_id,
                            scan_type_id=scan_type_id,
                            target_id=target_id,
                            target_type="repo",
                            vulnerabilityid=vulnerability["VulnerabilityID"],
                            pkgid=vulnerability["PkgID"],
                            pkg_name=vulnerability["PkgName"],
                            pkg_identifier=vulnerability["PkgIdentifier"],
                            installed_version=vulnerability["InstalledVersion"],
                            fixed_version=vulnerability.get("FixedVersion", ""),
                            status=vulnerability["Status"],
                            severity_source=vulnerability["SeveritySource"],
                            primary_url=vulnerability["PrimaryURL"],
                            data_source=vulnerability["DataSource"],
                            title=vulnerability["Title"],
                            severity=vulnerability["Severity"],
                            description=vulnerability["Description"],
                            # cwe_ids=vulnerability["CweIDs"],
                            vendor_severity=vulnerability["VendorSeverity"],
                            # CVSS=vulnerability["CVSS"],
                            references=json.dumps(vulnerability["References"]),
                            created=datetime.now(timezone.utc),
                            creator=current_user,
                        )
                        new_vulnerability_obj.save()
                        print("Vulnerability saved")
            
                if "Licenses" in data:
                    for license in data["Licenses"]:
                        new_license_obj = FindingLicense(
                            license_id=str(uuid.uuid4()),
                            project_id=project_id,
                            scan_type_id=scan_type_id,
                            target_id=target_id,
                            target_type="repo",
                            severity=license["Severity"],
                            category=license["Category"],
                            pkg_name=license["PkgName"],
                            file_path=license["FilePath"],
                            name=license["Name"],
                            text=license["Text"],
                            # confidence=license["Confidence"],
                            link=license["Link"],
                            created=datetime.now(timezone.utc),
                            creator=current_user,
                        )
                        new_license_obj.save()
                        print("License saved", license['Name'])
        except Exception as e:
            print(f"Unexpected error occurred while saving: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, '500 Internal Server Error'
        print("Trivy scan completed for license.")
        return {"message": "Trivy scan for License and SBOM completed and results saved."}, 200
    
    def run_cloudsploit(self, project_id, scan_id, azure_cloud_target_id, azure_cloud_data, azure_scanner_id, current_user, cloudsploit_config_path, cloudsploit_original_content):
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

        scanner_types = self.get_cloudsploit_scanner_types()
        azure_raw_op, azure_scan_json_data = run_azure_cloud_scan(project_id, scan_id, azure_cloud_data, azure_scanner_id, current_user, cloudsploit_config_path, cloudsploit_original_content)

        # Check if an error occurred (i.e., azure_raw_op contains an error message)
        if isinstance(azure_raw_op, dict) and "error" in azure_raw_op:
            print(f"Scan failed with error: {azure_raw_op['error']}")
            return azure_raw_op  # Return error details if any
    
        structured_azure_op = convert_structured_azure_output(azure_scan_json_data, scanner_types)
        azure_raw_data_str = json.dumps(azure_raw_op)
        try:
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=scan_id,
                output=azure_raw_data_str,
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            raw_scan_output_obj.save()
            raw_scan_output_details = json.loads(
                raw_scan_output_obj.to_json())
            print("raw scan result", raw_scan_output_details)
        except Exception as e:
            print("general exception", e)
            return None, f"Error saving findings: {e}"
        
        # input_text = "Cloud Vulnerability"
        # scan_type_id = findScanTypeId(input_text, 'scan_type')
        # Save structured findings to the database
        try:
            for result in structured_azure_op:
                cloud_cloudsploit_azure_1_details = result.get('cloud_cloudsploit_azure_1_record')

                is_found = findDuplicateFindingAndLink(project_id, azure_cloud_target_id, result.get('scan_type_id', ''), result.get('finding_name', ''), scan_id, current_user)
                if is_found:
                    continue

                cloud_cloudsploit_azure_obj = CloudCloudSploitAzure1(
                    cloud_azure_id=str(uuid.uuid4()),
                    plugin=cloud_cloudsploit_azure_1_details.get('plugin', ''),
                    category=cloud_cloudsploit_azure_1_details.get('category', ''),
                    description=cloud_cloudsploit_azure_1_details.get('description', ''),
                    resource=cloud_cloudsploit_azure_1_details.get('resource', ''),
                    region=cloud_cloudsploit_azure_1_details.get('region', ''),
                    status=cloud_cloudsploit_azure_1_details.get('status', ''),
                    message=cloud_cloudsploit_azure_1_details.get('message', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                cloud_cloudsploit_azure_obj.save()
                cloud_cloudsploit_azure_data = json.loads(cloud_cloudsploit_azure_obj.to_json())

                new_fix_recom_obj = FixRecommendations(
                    fix_recommendation_id=str(uuid.uuid4()),
                    scanner_fix=None,
                    ai_fix=None,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_fix_recom_obj.save()
                new_fix_recom_obj_data = json.loads(new_fix_recom_obj.to_json())

                findings_obj = FindingMaster(
                    finding_id=str(uuid.uuid4()),
                    project_id=project_id,
                    finding_date=datetime.now(timezone.utc),
                    target_id=azure_cloud_target_id,
                    target_type='cloud',
                    scan_type_id=result.get('scan_type_id', ''),
                    finding_name=result.get('finding_name', ''),
                    finding_desc=result.get('finding_desc', ''),
                    severity=result.get('severity', ''),
                    status=result.get('status', 'open'),
                    extended_finding_details_name='CloudCloudSploitAzure1',
                    extended_finding_details_id=cloud_cloudsploit_azure_data.get('_id', ''),
                    raw_scan_output_id=raw_scan_output_details.get('_id', ''),
                    fix_recommendation_id=new_fix_recom_obj_data.get('_id', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                findings_obj.save()
        except Exception as e:
            print(f"Unexpected error occurred while saving: {e}")
            return {"message": "CloudSploit scan for Azure failed.", "error": str(e)}, 500
        print("CloudSploit scan for Azure completed.")
        return {"message": "CloudSploit scan for Azure completed and results saved."}, 200
         
    def run_cloudsploit_for_google(self, project_id, scan_id, google_cloud_target_id, google_cloud_data, google_scanner_id, current_user, google_cloudsploit_config_path, google_cloudsploit_original_content):
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

        scanner_types = self.get_cloudsploit_scanner_types()
        google_raw_op, google_scan_json_data = run_google_cloud_scan(project_id, scan_id, google_cloud_data, google_scanner_id, current_user, google_cloudsploit_config_path, google_cloudsploit_original_content)

        # Check if an error occurred (i.e., google_raw_op contains an error message)
        if isinstance(google_raw_op, dict) and "error" in google_raw_op:
            print(f"Scan failed with error: {google_raw_op['error']}")
            return google_raw_op  
    
        structured_google_op = convert_structured_google_output(google_scan_json_data, scanner_types)
        google_raw_data_str = json.dumps(google_raw_op)
        try:
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=scan_id,
                output=google_raw_data_str,
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            raw_scan_output_obj.save()
            raw_scan_output_details = json.loads(
                raw_scan_output_obj.to_json())
            print("raw scan result", raw_scan_output_details)
        except Exception as e:
            print("general exception", e)
            return None, f"Error saving findings: {e}"
        
        # input_text = "Cloud Vulnerability"
        # scan_type_id = findScanTypeId(input_text, 'scan_type')
        # Save structured findings to the database
        try:
            for result in structured_google_op:
                cloud_cloudsploit_google_1_details = result.get('cloud_cloudsploit_google_1_record')

                is_found = findDuplicateFindingAndLink(project_id, google_cloud_target_id, result.get('scan_type_id', ''), result.get('finding_name', ''), scan_id, current_user)
                if is_found:
                    continue

                cloud_cloudsploit_google_obj = CloudCloudSploitGoogle1(
                    cloud_google_id=str(uuid.uuid4()),
                    plugin=cloud_cloudsploit_google_1_details.get('plugin', ''),
                    category=cloud_cloudsploit_google_1_details.get('category', ''),
                    title=cloud_cloudsploit_google_1_details.get('title', ''),
                    description=cloud_cloudsploit_google_1_details.get('description', ''),
                    resource=cloud_cloudsploit_google_1_details.get('resource', ''),
                    region=cloud_cloudsploit_google_1_details.get('region', ''),
                    status=cloud_cloudsploit_google_1_details.get('status', ''),
                    message=cloud_cloudsploit_google_1_details.get('message', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                cloud_cloudsploit_google_obj.save()
                cloud_cloudsploit_google_data = json.loads(cloud_cloudsploit_google_obj.to_json())

                new_fix_recom_obj = FixRecommendations(
                    fix_recommendation_id=str(uuid.uuid4()),
                    scanner_fix=None,
                    ai_fix=None,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                new_fix_recom_obj.save()
                new_fix_recom_obj_data = json.loads(new_fix_recom_obj.to_json())

                findings_obj = FindingMaster(
                    finding_id=str(uuid.uuid4()),
                    project_id=project_id,
                    finding_date=datetime.now(timezone.utc),
                    target_id=google_cloud_target_id,
                    target_type='cloud',
                    scan_type_id=result.get('scan_type_id', ''),
                    finding_name=result.get('finding_name', ''),
                    finding_desc=result.get('finding_desc', ''),
                    severity=result.get('severity', ''),
                    status=result.get('status', 'open'),
                    extended_finding_details_name='CloudCloudSploitGoogle1',
                    extended_finding_details_id=cloud_cloudsploit_google_data.get('_id', ''),
                    raw_scan_output_id=raw_scan_output_details.get('_id', ''),
                    fix_recommendation_id=new_fix_recom_obj_data.get('_id', ''),
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                findings_obj.save()
            print("CloudSploit scan for Google completed.")
            return {"message": "CloudSploit scan for Google completed and results saved."}, 200
        except Exception as e:
            print(f"Unexpected error occurred while saving: {e}")
            return {"message": "CloudSploit scan for Google failed.", "error": str(e)}, 500
         
    def fetch_by_project_id(self, fields) -> List[dict]:
        """
        Fetches a scans object by its project_id from the database,
        including scheduler data and scanner type details.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        if "project_id" in fields:
            project_id = fields['project_id']

            try:
                pipeline = [
                    # Match scans by project_id
                    {
                        "$match": {
                            "project_id": project_id
                        }
                    },
                    # Lookup data from the Scheduler collection
                    {
                        "$lookup": {
                            "from": "Scheduler",  # Name of the Scheduler collection
                            "localField": "scheduler_id",  # Field in Scans collection
                            "foreignField": "_id",  # Field in Scheduler collection
                            "as": "scheduler_data"  # Field to store joined data
                        }
                    },
                    # Unwind the scheduler_data array to simplify further operations
                    {
                        "$unwind": {
                            "path": "$scheduler_data",
                            "preserveNullAndEmptyArrays": True  # Optional: include records with no matching scheduler
                        }
                    },
                    {
                        "$unwind": {
                            "path": "$scheduler_data.scanner_type_ids_list",
                            "preserveNullAndEmptyArrays": True # Handle cases where the list is empty
                        }
                    },
                    # Lookup corresponding scanner type details for each scanner_type_ids_list element
                    {
                        "$lookup": {
                            "from": "ScannerTypes",  # Name of the ScannerType collection
                            "localField": "scheduler_data.scanner_type_ids_list",  # Field with scanner UUIDs
                            "foreignField": "_id",  # Field in ScannerType collection
                            "as": "scanner_type_details"  # Field to store the detailed data
                        }
                    },
                    # Transform scanner_type_details to only include the scan_type field
                    {
                        "$addFields": {
                            "scanner_type_details": {
                                "$map": {
                                    "input": "$scanner_type_details",  # The array of scanner type objects
                                    "as": "scanner",
                                    "in": "$$scanner.scan_type"  # Extract only the scan_type field
                                }
                            }
                        }
                    },
                    # Group the data back into the desired format
                    {
                        "$group": {
                            "_id": "$_id",
                            "created": {"$first": "$created"},
                            "creator": {"$first": "$creator"},
                            "duration": {"$first": "$duration"},
                            "execution_date": {"$first": "$execution_date"},
                            "project_id": {"$first": "$project_id"},
                            "scheduler_data": {"$first": "$scheduler_data"},
                            "scanner_type_details": {"$push": "$scanner_type_details"}, # Already mapped to scan_type
                            "scheduler_id": {"$first": "$scheduler_id"},
                            "status": {"$first": "$status"},
                            "updated": {"$first": "$updated"},
                            "updator": {"$first": "$updator"}
                        }
                    },
                    {
                        "$addFields": {
                            "scanner_type_details": {
                                "$reduce": {
                                    "input": "$scanner_type_details",
                                    "initialValue": [],
                                    "in": {"$concatArrays": ["$$value", "$$this"]}
                                }
                            }
                        }
                    },
                    # Exclude sensitive or unwanted fields
                    {
                        "$project": {
                            "isdeleted": 0,  # Example: Exclude the isdeleted field
                            "some_other_field": 0  # Replace with other fields to exclude
                        }
                    }
                ]



                # Execute the aggregation pipeline
                scans_results_list = list(
                    Scans.objects.aggregate(*pipeline)
                )

                return {'success': 'Records fetched successfully', 'data': scans_results_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def run_linguist(self, project_id, scan_id, target_id, repo_path, current_user, linguist_id):
        print("Starting GitHub Linguist scan...")
        print(f"Project ID: {project_id}, Scan ID: {scan_id}, Target ID: {target_id}, Repo Path: {repo_path}, Linguist ID: {linguist_id}, User: {current_user}")
        
        try:
            # Step 1: Run GitHub Linguist
            print("Executing GitHub Linguist command...")
            linguist_output = os.popen(f"github-linguist {repo_path} --json").read()
            print("Linguist command executed successfully.")
        except Exception as e:
            print(f"Error running GitHub Linguist: {e}")
            return {'error': f'Error running GitHub Linguist: {e}'}, '500 Internal Server Error'

        try:
            # Step 2: Parse the JSON output
            print("Parsing Linguist output...")
            linguist_data = json.loads(linguist_output)
            print("Linguist output parsed successfully.")
            
            # Step 3: Save raw scan output
            print("Saving raw scan output...")
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=linguist_id,
                output=linguist_output,
                created=datetime.now(timezone.utc),
                creator=current_user
            )
            raw_scan_output_obj.save()
            print(f"Linguist Raw scan output saved: {raw_scan_output_obj}")
            
            # Step 4: Process Linguist data
            for language_name, language_data in linguist_data.items():
                print(f"Processing language: {language_name}")
                language_count = language_data.get('size', 0)
                language_percentage = float(language_data.get('percentage', 0))

                input_text = 'Languages and Framework'
                scan_type_id = findScanTypeId(input_text, 'scan_type')
                print(f"Scan type ID found: {scan_type_id}")

                # Check for duplicate findings and mark as deleted if found
                print(f"Checking for duplicate findings for {language_name}...")
                duplicate_found = findDuplicateFindingAndLinkForLanguages(project_id, target_id, scan_type_id, language_name)

                # Create a new LanguagesAndFramework object
                print(f"Saving LanguagesAndFramework object for {language_name}...")
                languages_and_framework_obj = LanguagesAndFramework(
                    languages_and_framework_id=str(uuid.uuid4()),
                    project_id=project_id,
                    finding_date=datetime.now(timezone.utc),
                    target_id=target_id,
                    scan_type_id=scan_type_id,
                    language_name=language_name,
                    language_count=language_count,
                    language_percentage=language_percentage,
                    raw_scan_output_id=raw_scan_output_obj.raw_scan_output_id,
                    created=datetime.now(timezone.utc),
                    creator=current_user
                )
                languages_and_framework_obj.save()
                print(f"Saved LanguagesAndFramework object for {language_name}.")
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {'error': f'JSON parsing error: {e}'}, '400 Bad Request'
        except DoesNotExist as e:
            print(f"Database query error: {e}")
            return {'error': f'Database query error: {e}'}, '404 Not Found'
        except ValidationError as e:
            print(f"Validation error: {e.message}")
            return {'error': f'Validation error: {e.message}'}, '400 Bad Request'
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {'error': f'Unexpected error: {e}'}, '500 Internal Server Error'

        print("Completed GitHub Linguist scan.")
        return {'message': 'Linguist scan completed successfully'}, '200 OK'
    
    def run_slither(self, project_id, scan_id, repo_target_id, slither_scanner_id, current_user):
        """
        Run a Slither scan, process the results, and save findings to the database.
        Dynamically handles dependencies, including npm libraries, GitHub repositories, and local imports.
        """
        temp_dir = None  # Initialize temp_dir for later cleanup
        try:
            print("INFO: Smart contract scanner triggered.")
            temp_dir = tempfile.mkdtemp()
            print(f"INFO: Contracts directory set to '{temp_dir}'.")

            # Collect Solidity files to process
            files_to_process = []
            dependencies = set()
            print(f"INFO: Fetching contracts for project ID: {project_id}.")
            for contract in Contract.objects(project_id=project_id):
                print(f"INFO: Processing contract ID: {contract.id}.")
                for file_entry in contract.solidity_files:
                    try:
                        print(f"INFO: Processing Solidity file: {file_entry.file_name}.")
                        file_content = base64.b64decode(file_entry.file_content).decode('utf-8')
                        file_name = file_entry.file_name

                        # Extract the Solidity version
                        solidity_version = extract_solidity_version(file_content)
                        if not solidity_version:
                            print(f"WARNING: Could not determine Solidity version in {file_name}. Skipping file.")
                            continue

                        print(f"INFO: Solidity version found in {file_name}: {solidity_version}.")
                        if file_entry.file_path:
                            file_path = os.path.join(temp_dir, file_entry.file_path)
                        else:
                            file_path = os.path.join(temp_dir, file_name)

                        # Create necessary directories
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)

                        # Save the Solidity file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(file_content)
                        print(f"INFO: File saved at path: {file_path}. File exists: {os.path.exists(file_path)}")

                        files_to_process.append(file_path)

                    except Exception as file_error:
                        print(f"ERROR: Error processing file {file_name}: {file_error}")
                        continue  # Log error and continue

            if not files_to_process:
                return {'error': 'No valid Solidity files to process.'}, 400

            # Detect dependencies from Solidity files
            dependencies = detect_imported_dependencies(temp_dir)

            # Install dependencies dynamically
            print("INFO: Installing Solidity dependencies.")
            install_dependencies(temp_dir, dependencies)

            # Resolve local imports
            print("INFO: Resolving local imports.")
            resolve_local_imports(temp_dir)

            # Install the required Solidity version using solc-select
            subprocess.run(["solc-select", "install", solidity_version], check=True)

            # Prepare Slither project file
            print(f"INFO: Preparing project directory at {temp_dir} for Slither.")
            project_sources = {file: {} for file in files_to_process}
            with open(os.path.join(temp_dir, "slither.project.json"), "w", encoding="utf-8") as project_file:
                project_file.write(json.dumps({"sources": project_sources}))

            # Construct the Slither command
            slither_command = (
                f"slither {temp_dir} --json - "
                f"--solc-remaps \"@={temp_dir}/node_modules/@\" "
                f"--solc-solcs-select {solidity_version}"
            )

            print(f"INFO: Executing Slither command: {slither_command}")

            # Execute Slither command
            try:
                result = subprocess.run(slither_command, shell=True, capture_output=True, text=True)
            # if result.returncode != 0:
            #     print(f"ERROR: Slither execution failed: {result.stderr}")
            #     return {'error': f"Error during Slither execution: {result.stderr}"}, 500

                slither_output = result.stdout
                if not slither_output:
                    print("ERROR: No output received from Slither.")
                    return {'error': 'No output received from Slither.'}, 500

                print("INFO: Slither scan completed successfully.")
                print(f"DEBUG: Slither output: {slither_output}")

                # Parse Slither output as JSON
                slither_data = json.loads(slither_output)

                # slither_raw_output = json.dumps(slither_data)
                chunks = chunk_data(slither_data)

            except Exception as e:
                print(f"ERROR: Slither execution failed: {e}")
                return {'error': f"Error during Slither execution: {str(e)}"}, 500

            # Save the raw scan output to the database
            raw_scan_output_obj = RawScanOutput(
                raw_scan_output_id=str(uuid.uuid4()),
                scan_id=scan_id,
                scanner_id=slither_scanner_id,
                output=slither_output,
                created=datetime.now(timezone.utc),
                creator=current_user
            )
            raw_scan_output_obj.save()
            new_slither_raw_scan_data = json.loads(raw_scan_output_obj.to_json())
            print("INFO: Slither raw scan output saved to database.")

            findings_data = []

            # Iterate directly over chunks
            for chunk in chunks:
                gpt_output = process_smart_contract_with_gpt([chunk], 1)
                if gpt_output:
                    findings_data.append(gpt_output)

            # Flatten findings_data into a single list of dictionaries
            flattened_findings = [finding for sublist in findings_data for finding in sublist]

            # Save findings, details, and fix recommendations in the database
            try:
                for result in flattened_findings:
                    input_text = result.get('finding_name')
                    scan_type_id = findScanTypeId(input_text, 'scan_type')

                    # If the result is 'others', fallback to "Smart Contract Vulnerability Scanner"
                    if scan_type_id == 'others':
                        scan_type_id = findScanTypeId("Smart Contract Vulnerability Scanner", 'scan_type')

                    is_found = findDuplicateFindingAndLinkForSmartContract(project_id, repo_target_id, scan_type_id, result.get('finding_name', ''), result.get('detailed_findings', []), scan_id, current_user)
                    if is_found:
                        continue

                    print(f"INFO: Saving finding: {result.get('finding_name')}")
                    fix_recom_obj = FixRecommendations(
                        fix_recommendation_id=str(uuid.uuid4()),
                        scanner_fix=result.get('issue_remediation', ''),
                        ai_fix=None,
                        created=datetime.now(timezone.utc),
                        creator=current_user
                    )
                    fix_recom_obj.save()
                    new_fix_recom_data = json.loads(fix_recom_obj.to_json())
                    print("INFO: Fix recommendation saved.")

                    for detail in result.get('detailed_findings', []):
                        slither_detail_obj = RepoSmartContractSlither1(
                            repo_smart_contract_slither_1_id=str(uuid.uuid4()),
                            issue_type=detail.get('issue_type', ''),
                            line_number=detail.get('line_number', ''),
                            contract=detail.get('contract', ''),
                            function=detail.get('function', ''),
                            source_code_snippet=detail.get('source_code_snippet', ''),
                            cwe_id=detail.get('cwe_id', ''),
                            references=detail.get('references', ''),
                            created=datetime.now(timezone.utc),
                            creator=current_user
                        )
                        slither_detail_obj.save()
                        new_slither_detail_data = json.loads(slither_detail_obj.to_json())
                        print(f"INFO: Slither detail finding saved for issue type: {detail.get('issue_type')}")

                        scan_type_id = findScanTypeId(result.get('finding_name', ''), 'scan_type')

                        # If the result is 'others', fallback to "Smart Contract Vulnerability Scanner"
                        if scan_type_id == 'others':
                            scan_type_id = findScanTypeId("Smart Contract Vulnerability Scanner", 'scan_type')

                        findings_obj = FindingMaster(
                            finding_id=str(uuid.uuid4()),
                            project_id=project_id,
                            finding_date=datetime.now(timezone.utc),
                            target_id=repo_target_id,
                            target_type='web3',
                            scan_type_id=scan_type_id,
                            finding_name=result.get('finding_name', ''),
                            finding_desc=result.get('issue_detail', '')[:255],
                            severity=result.get('risk_level', 'low').lower(),
                            status=result.get('status', 'open').lower(),
                            raw_scan_output_id=new_slither_raw_scan_data.get('_id', ''),
                            extended_finding_details_name='RepoSmartContractSlither1',
                            extended_finding_details_id=new_slither_detail_data.get('_id', ''),
                            fix_recommendation_id=new_fix_recom_data.get('_id', ''),
                            created=datetime.now(timezone.utc),
                            creator=current_user
                        )
                        findings_obj.save()
                        print(f"INFO: Slither main finding saved with name: {result.get('finding_name')}.")
            except Exception as e:
                print(f"ERROR: Error saving findings to the database: {e}")
                return {'error': f"Error saving findings: {e}"}, 500

            return {"message": "Slither scan completed and results saved."}, 200
        except Exception as e:
                print(f"ERROR: : {e}")
                return {'error': f"Error saving findings: {e}"}, 500
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir)
                print("INFO: Temporary files cleaned up.")

    