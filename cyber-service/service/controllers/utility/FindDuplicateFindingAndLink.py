from entities.CyberServiceEntity import FindingMaster, FindingScanLink, LanguagesAndFramework, RepoSmartContractSlither1
from mongoengine import DoesNotExist
import uuid, json
from datetime import datetime, timezone

def findDuplicateFindingAndLink(project_id, target_id, scan_type_id, finding_name, scan_id, current_user):
    try:
        finding_master = FindingMaster.objects.filter(
            project_id=project_id,
            target_id=target_id,
            scan_type_id=scan_type_id,
            finding_name=finding_name
        ).first()

        if finding_master:
            finding_master_json = json.loads(finding_master.to_json())

            if finding_master_json.get('status', '') == 'closed':
                finding_master.status = 'open'  

            finding_scan_obj = FindingScanLink(
                finding_scan_link_id=str(uuid.uuid4()),
                finding_id=finding_master_json.get('_id', ''),
                scan_id=scan_id,
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            
            finding_master.save()
            finding_scan_obj.save()
            return True
        else:
            print("No matching record found in FindingMaster.")
            return False

    except Exception as e:
        print("Exception: finding duplicate", e)
        return False
    
def findDuplicateFindingAndLinkForSmartContract(project_id, target_id, scan_type_id, finding_name, detailed_findings, scan_id, current_user):
    try:
        finding_master = FindingMaster.objects.filter(
            project_id=project_id,
            target_id=target_id,
            scan_type_id=scan_type_id,
            finding_name__icontains=finding_name,
        ).first()

        if finding_master:
            finding_master_json = json.loads(finding_master.to_json())

            # Extract extended finding details ID
            extended_finding_details_id = finding_master_json.get('extended_finding_details_id', None)
            line_number_match = False

            if extended_finding_details_id and detailed_findings:
                # Iterate through the list of detailed findings to check line_number matches
                for finding in detailed_findings:
                    line_number = finding.get("line_number")
                    if line_number:
                        extended_details = RepoSmartContractSlither1.objects.filter(
                            repo_smart_contract_slither_1_id=extended_finding_details_id,
                            line_number=line_number
                        ).first()
                        if extended_details:
                            line_number_match = True
                            break

            # Check finding_name match
            finding_name_match = finding_master_json.get('finding_name') == finding_name

            # Proceed if either condition matches
            if line_number_match or finding_name_match:
                if finding_master_json.get('status', '') == 'closed':
                    finding_master.status = 'open'

                finding_scan_obj = FindingScanLink(
                    finding_scan_link_id=str(uuid.uuid4()),
                    finding_id=finding_master_json.get('_id', ''),
                    scan_id=scan_id,
                    created=datetime.now(timezone.utc),
                    creator=current_user,
                )

                finding_master.save()
                finding_scan_obj.save()
                return True

            print("No matching line_number or finding_name found.")
            return False
        else:
            print("No matching record found in FindingMaster.")
            return False

    except Exception as e:
        print("Exception: Duplicate entries found in the smart contract", e)
        return False
      
def findDuplicateFindingAndLinkForLanguages(project_id, target_id, scan_type_id, language_name):
    try:
        print(f"Checking for duplicates: project_id={project_id}, target_id={target_id}, scan_type_id={scan_type_id}, language_name={language_name}")
        
        # Aggregation pipeline to find duplicate records
        pipeline = [
            {
                "$match": {
                    "project_id": project_id,
                    "target_id": target_id,
                    "scan_type_id": scan_type_id,
                    "language_name": language_name
                }
            },
            {
                "$limit": 1
            }
        ]
        
        language_findings = list(LanguagesAndFramework.objects.aggregate(*pipeline))
        
        # If duplicates are found, mark them as deleted
        if language_findings:
            print(f"Duplicate found for language '{language_name}'. Marking as deleted.")
            LanguagesAndFramework.objects.filter(
                project_id=project_id,
                target_id=target_id,
                scan_type_id=scan_type_id,
                language_name=language_name
            ).update(isdeleted=True)
        else:
            print(f"No duplicates found for language '{language_name}'.")
            
    except Exception as e:
        print(f"Exception while finding duplicates for language '{language_name}': {e}")

