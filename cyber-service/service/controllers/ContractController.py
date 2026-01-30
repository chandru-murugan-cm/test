import base64
from controllers.util import *
from entities.CyberServiceEntity import Contract, FileEntry, FindingMaster, RepoSmartContractSlither1, FixRecommendations
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from mongoengine import *
from marshmallow import Schema, fields, ValidationError, INCLUDE
from datetime import datetime, timezone
from typing import List
from bson import ObjectId
import uuid
import json
import os
import zipfile
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'sol', 'zip'}
UPLOAD_FOLDER = 'uploads'

class ContractAddSchema(Schema):
    project_id = fields.String(required=True, error_messages={
        "required": "Project ID is required."})
    contract_url = fields.String(null=True, error_messages={
        "required": "Contract URL is missing."})
    contract_label = fields.String(null=True, error_messages={
        "required": "Contract Label is missing."})


class ContractUpdateSchema(Schema):
    contract_url = fields.String(null=True, error_messages={
        "required": "Contract URL is missing."})
    contract_label = fields.String(null=True, error_messages={
        "required": "Contract Label is missing."})


class ContractController:
    """
    Defines controller methods for the Contract Entity.
    """

    def __init__(self) -> None:
        pass

    def _validateContractAdd(self, request_json):
        schema = ContractAddSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'Validation successful'}, '200 Ok'

    def _validateContractUpdate(self, request_json):
        schema = ContractUpdateSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'Validation successful'}, '200 Ok'

    def _validateContract(self, contract_id):
        """
        Validates contract id with the database.
        """
        try:
            Contract.objects.get(target_contract_id=contract_id)
            return True, {'message': 'Record exists in db'}, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the contract objects from the database. 
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        pipeline = [
            {
                "$match": {
                    **fields
                }
            },
            {
                "$project": {
                    "isdeleted": 0,
                }
            }
        ]

        # Execute the aggregation pipeline
        contract_list = list(Contract.objects.aggregate(pipeline))
        response = contract_list
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'

    def update_by_id(self, request, target_contract_id) -> dict:
        """
        Updates a contract object by its ID, updating only the fields provided in the request.
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        # Get the JSON data from the request
        request_json = request.get_json()

        # Validate the contract update
        status, result, status_code = self._validateContractUpdate(request_json)
        if not status:
            return jsonify(result), status_code

        # Validate contract ID
        if target_contract_id != request_json.get('target_contract_id'):
            return {'error': 'Contract ID in URL does not match the provided target_contract_id in the body'}, '400 Bad Request'

        print(f"Contract ID mismatch: URL ID ({target_contract_id}) != Body ID ({request_json.get('target_contract_id')})")
        try:
            # Fetch the contract from the database
            contract_obj = Contract.objects.get(target_contract_id=target_contract_id)

            if 'contract_url' in request_json:
                contract_obj['contract_url'] = request_json['contract_url']
                contract_obj['contract_label'] = request_json['contract_label']

            # Handle file uploads
            if 'solidity_files' in request.files:
                solidity_files = request.files.getlist('solidity_files')
                saved_files = []
                for file in solidity_files:
                    if file and self._allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(file_path)
                        saved_files.append(file_path)
                contract_obj['solidity_files'] = saved_files

            contract_obj['updator'] = current_user
            contract_obj['updated'] = datetime.now(timezone.utc)

            contract_obj.save()
            response = json.loads(contract_obj.to_json())

            return {'success': 'Record updated successfully', 'data': response}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'Contract not found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'

    def add_entity(self, request) -> dict:
        """
        Creates a new contract object in the database, handling both .sol files and .zip files containing .sol files.
        Excludes macOS and Windows system files like '__MACOSX', 'Thumbs.db', and 'desktop.ini'.
        """
        current_user = get_current_user_from_jwt_token()
        
        # Check for file part in request
        if 'files' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        project_id = request.form.get('project_id')

        if not project_id:
            return jsonify({'error': 'Project ID is required'}), 400
        
        contract_url = request.form.get('contract_url') or ''

        # if not contract_url:
        #     return jsonify({'error': 'Contract URL is required'}), 400
        
        contract_label = request.form.get('contract_label')

        if not contract_label:
            return jsonify({'error': 'Contract Label is required'}), 400

        # Validate contract data
        status, result, status_code = self._validateContractAdd(request.form)
        if not status:
            return jsonify(result), status_code        

        try:
            # Create a new Contract object
            new_contract_obj = Contract(
                target_contract_id=str(uuid.uuid4()),
                project_id=project_id,
                contract_url=contract_url,
                contract_label=contract_label,
                created=datetime.now(timezone.utc),
                creator=current_user,
            )

            # Handle multiple file uploads
            uploaded_files = request.files.getlist('files')
            
            for file in uploaded_files:
                # If the uploaded file is a .zip
                if file.filename.endswith('.zip'):
                    # Normalize the zip file name (remove spaces)
                    zip_name = os.path.splitext(file.filename)[0].replace(' ', '')
                    # Unzip the file in memory
                    with zipfile.ZipFile(file, 'r') as zip_ref:
                        # Extract files and save them to the database
                        for file_name in zip_ref.namelist():
                            # Skip files that are system files or hidden (e.g. from macOS or Windows)
                            if any(prefix in file_name for prefix in ['__MACOSX', 'Thumbs.db', 'desktop.ini', '$RECYCLE.BIN']):
                                continue

                            # Ensure we process only .sol files
                            if file_name.endswith('.sol'):
                                file_content = zip_ref.read(file_name)  # Read file content as bytes

                                # Encode the file content into base64
                                encoded_content = base64.b64encode(file_content).decode('utf-8')  # Convert to base64 string

                                # Check if file_name contains any directory structure
                                file_dir = os.path.dirname(file_name)
                                if not file_dir:  # If no directory structure, prepend zip_name
                                    file_path = os.path.join(zip_name, file_name)
                                else:  # Keep the directory structure as is
                                    file_path = os.path.join(zip_name, file_name)

                                # Prepare file entry
                                file_entry = FileEntry(
                                    file_id=file,  # Store the file object or a unique identifier
                                    file_name=file_name,
                                    file_content=encoded_content,  # Store as base64-encoded string
                                    created=datetime.now(timezone.utc),
                                    file_path=file_path,  # Folder structure (if any)
                                )
                                new_contract_obj.solidity_files.append(file_entry)
                else:
                    # Process a single .sol file
                    if file.filename.endswith('.sol'):
                        # Skip any non-.sol files
                        file_content = file.read()  # Read file content as bytes
                        
                        # Encode the file content into base64
                        encoded_content = base64.b64encode(file_content).decode('utf-8')  # Convert to base64 string
                        
                        # Prepare file entry for single file
                        file_entry = FileEntry(
                            file_id=file,  # Use a unique identifier for file storage
                            file_name=file.filename,
                            file_content=encoded_content,  # Store as base64-encoded string
                            created=datetime.now(timezone.utc),
                            file_path='',  # No path for individual files
                        )
                        new_contract_obj.solidity_files.append(file_entry)

            # Save the new contract object
            new_contract_obj.save()

            return {
                'success': 'Record Created Successfully',
                'contract_id': new_contract_obj.target_contract_id,
            }, '200 Ok'

        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except Exception as e:
            return {'error': 'An error occurred while processing the files: ' + str(e)}, '500 Internal Server Error'


    def view_uploaded_files(self, contract_id):
        """
        Retrieves and views the uploaded file details for a given contract ID.
        """
        try:
            contract = Contract.objects.get(target_contract_id=contract_id)
            file_details = []

            # Iterate over all files in the contract
            for file_entry in contract['solidity_files']:
                file_details.append({
                    'file_name': file_entry['file_name'],
                    'file_content': file_entry['file_content']  # Return stored file content
                })

            return {
                'success': True,
                'files': file_details
            }

        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}


    def remove_entity(self, contract_id):
        """
        Removes the Contract object from the database.
        """
        # Validates the JWT Token
        verify_jwt_in_request()
        try:
            # Convert string to ObjectId if needed
            contract_obj = Contract.objects.get(target_contract_id=contract_id)
            if not contract_obj:
                return {'error': 'No contract record found with the given ID' +str(contract_id)}, '404 Not Found'
           
            # Optionally, mark as deleted without removing from the database (soft delete)
            finding_master_queryset = FindingMaster.objects(target_id=contract_id)
            for finding in finding_master_queryset:
                try:
                    # Fetch Slither scan output related object and mark as deleted
                    repo_smart_contract_obj = RepoSmartContractSlither1.objects.get(repo_smart_contract_slither_1_id=finding.extended_finding_details_id)
                    repo_smart_contract_obj.isdeleted = True
                    repo_smart_contract_obj.deleted_at = datetime.now(timezone.utc)
                    repo_smart_contract_obj.save()
                    print(f"Deleted RepoSmartContractSlither1 record with repo_smart_contract_slither_1_id: {repo_smart_contract_obj.repo_smart_contract_slither_1_id}")
                except RepoSmartContractSlither1.DoesNotExist:
                    print(f"RepoSmartContractSlither1 record with repo_smart_contract_slither_1_id {finding.extended_finding_details_id} not found")

                try:
                    # Fetch Fix recommendation related object and mark as deleted
                    fix_recom_obj = FixRecommendations.objects.get(fix_recommendation_id=finding.fix_recommendation_id)
                    fix_recom_obj.isdeleted = True
                    fix_recom_obj.deleted_at = datetime.now(timezone.utc)
                    fix_recom_obj.save()
                    print(f"Deleted FixRecommendations record with fix_recommendation_id: {fix_recom_obj.fix_recommendation_id}")
                except FixRecommendations.DoesNotExist:
                    print(f"FixRecommendations record with target id {finding.fix_recommendation_id} not found")

                # Update each object in the FindingMaster queryset
                finding.isdeleted = True
                finding.deleted_at = datetime.now(timezone.utc)
                finding.save()
                print(f"Deleted FindingMaster record with ID: {finding.id}")

            # Mark the Smart Contract object as deleted
            contract_obj.isdeleted = True
            contract_obj.deleted_at = datetime.now(timezone.utc)
            contract_obj.save()

            # Print the deletion details for Smart Contract
            print(f"Deleted Smart Contract record with contract id: {contract_id}")

            return {'success': f'Smart Contract record with ID {contract_id} has been marked as deleted'}, '200 Ok'

        except Contract.DoesNotExist as e:
            print("Error deleting Smart Contract record: ", e)
            return {'error': f'Smart Contract record with ID {contract_id} not found'}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except Exception as e:
            print("Error deleting Smart Contract record: ", e)
            return {'error': 'Error deleting Smart Contract record: ' + str(e)}, '500 Internal Server Error'

    def _allowed_file(self, filename):
        """
        Check if the file extension is allowed.
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
