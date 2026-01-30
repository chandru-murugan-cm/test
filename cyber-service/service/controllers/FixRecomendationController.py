from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import Contract, Domain, DomainWapiti1, DomainZap1, FindingMaster, FixRecommendations, RepoSecretDetections, Repository, RepositoryTrivy1, ScanTargetType, ScannerTypes, RepoSmartContractSlither1, CloudCloudSploitAzure1, CloudCloudSploitGoogle1, TargetAzureCloud, TargetGoogleCloud
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')

# Set your OpenAI API key
client = OpenAI(api_key=openai_api_key)

class FixRecomendationController():
    """
    Defines controller methods for the Fix Remcomendation Entity.
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches a Fix Recomendation object by its _id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "_id" in fields:
            fix_recomendation_id = fields['_id']

            try:
                #Query Fix-Recommendation record (by fix_recommendation_id) - starts
                pipeline = [
                    {
                        "$match": {
                            "_id": fix_recomendation_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0
                        }
                    }
                ]
                # Execute the aggregation pipeline
                fix_recomendation_list = list(
                    FixRecommendations.objects.aggregate(*pipeline)
                )
                fix_recommendation_object = fix_recomendation_list[0] if fix_recomendation_list else {}
                #Query Fix-Recommendation record (by fix_recommendation_id) - ends
                if fix_recommendation_object.get('ai_fix') is None:
                    print("ai_fix is null.",fix_recomendation_id)
                    finding_master_record = FindingMaster.objects.get(fix_recommendation_id=fix_recomendation_id)
                    print("scan_type_id",finding_master_record.scan_type_id)
                    scan_type = ScannerTypes.objects.get(scan_type_id=finding_master_record.scan_type_id)
                   
                    target=None
                    print("target_id",finding_master_record.target_id)
                    print("scan_target_type",scan_type.scan_target_type)
                    if scan_type.scan_target_type is ScanTargetType.DOMAIN:
                        target = Domain.objects.get(target_domain_id=finding_master_record.target_id)
                    if scan_type.scan_target_type is ScanTargetType.REPO:
                        target = Repository.objects.get(target_repository_id=finding_master_record.target_id)
                    if scan_type.scan_target_type is ScanTargetType.WEB3:
                        target = Contract.objects.get(target_contract_id=finding_master_record.target_id)
                    if scan_type.scan_target_type is ScanTargetType.CLOUD:
                        if finding_master_record.extended_finding_details_name in ['CloudCloudSploitGoogle1']:
                            target = TargetGoogleCloud.objects.get(google_id=finding_master_record.target_id)
                        elif finding_master_record.extended_finding_details_name in ['CloudCloudSploitAzure1']:
                            target = TargetAzureCloud.objects.get(azure_id=finding_master_record.target_id)

                    print("extended_finding_details_name",finding_master_record.extended_finding_details_name)
                    print("inside extended_finding_details_id", finding_master_record.extended_finding_details_id)
                    extended_finding_details =None
                    if finding_master_record.extended_finding_details_name == 'DomainZap1':
                        extended_finding_details = DomainZap1.objects.get(domain_zap_1_id=finding_master_record.extended_finding_details_id)
                    if finding_master_record.extended_finding_details_name == 'DomainWapiti1':
                        extended_finding_details = DomainWapiti1.objects.get(domain_wapiti_1_id=finding_master_record.extended_finding_details_id)
                    if finding_master_record.extended_finding_details_name == 'RepoSecretDetections':
                        extended_finding_details = RepoSecretDetections.objects.get(repo_secret_detections_id=finding_master_record.extended_finding_details_id)
                    if finding_master_record.extended_finding_details_name == 'RepositoryTrivy1':
                        extended_finding_details = RepositoryTrivy1.objects.get(repository_trivy_1_id=finding_master_record.extended_finding_details_id)
                    if finding_master_record.extended_finding_details_name == 'RepoSmartContractSlither1':
                        extended_finding_details = RepoSmartContractSlither1.objects.get(repo_smart_contract_slither_1_id=finding_master_record.extended_finding_details_id)
                    if finding_master_record.extended_finding_details_name == 'CloudCloudSploitAzure1':
                        extended_finding_details = CloudCloudSploitAzure1.objects.get(cloud_azure_id=finding_master_record.extended_finding_details_id)
                    if finding_master_record.extended_finding_details_name == 'CloudCloudSploitGoogle1':
                        extended_finding_details = CloudCloudSploitGoogle1.objects.get(cloud_google_id=finding_master_record.extended_finding_details_id)
                    
                    # Function to generate a prompt from any given issue object
                    print(finding_master_record.to_json())
                    def generate_prompt():
                        prompt = f"Here is the details of cybersecurity issue in my application:\n\n {finding_master_record.to_json()} {scan_type.to_json()} {target.to_json()} {extended_finding_details.to_json()} \nPlease provide a ONLY the recommended fix this issue, point-out where the fix is, also provide a sample code."
                        print("promt", prompt)
                        return prompt

                    # # Generate the prompt dynamically based on the structure of the issue object
                    prompt = generate_prompt()

                    # Correct API call using the new structure for openai API >= 1.0.0
                    response = client.chat.completions.create(
                        model="gpt-4o",  # Or gpt-3.5-turbo depending on your preference
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                    )

                    # Print the response from OpenAI
                    print("Message", response.choices[0].message)

                    fix_recommendation_object['ai_fix'] = response.choices[0].message.content

                    FixRecommendations.objects.filter(fix_recommendation_id=fix_recomendation_id).update_one(
                        set__ai_fix=fix_recommendation_object['ai_fix']
                    )
                    return {'success': 'Records fetched scan_type', 'data': fix_recommendation_object}, '200 Ok'
                else:
                    return {'success': 'Records fetched successfully', 'data': fix_recommendation_object}, '200 Ok'
            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
