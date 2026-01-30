from entities.CyberServiceEntity import FindingLicensesAndSbom, FindingLicense, FindingSBOMVulnerability
from flask_jwt_extended import verify_jwt_in_request
from mongoengine import DoesNotExist

class RepoScanResultsController:
    """
    Defines controller methods for the getting Licenses and SBOM from the repo scan by trivy.
    """

    def __init__(self) -> None:
        pass

    def fetch_licenses_and_sbom(self, request, fields):
        """
        Fetches all the licenses and SBOM objects by project id from the database and generates
        elaborate statistical counts for licenses, severities, package names, and other relevant data.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        project_id = fields.get('project_id', '')

        if not project_id:
            return {'error': 'Project ID is required'}, '400 Bad Request'

        try:
            # Create the aggregation pipeline
            pipeline = [
                {"$match": {
                    "project_id": project_id,
                    "$or": [
                        {"isdeleted": None}  
                    ]
                }},
                {"$sort": {"created": -1}},  
            ]

            # Execute the aggregation pipeline
            findings = list(FindingLicense.objects.aggregate(*pipeline))
            print("findings", findings)

            # If no records found, return an appropriate message
            if not findings:
                return {'error': 'No records found for the provided project_id'}, '200 Ok'
            
            # Initialize statistics counters
            license_stats = {}
            severity_stats = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0, 'UNKNOWN': 0}
            package_stats = {}
            no_assertion_count = 0
            unknown_severity_count = 0
            total_packages = 0

            # Iterate through findings to calculate the counts
            for finding in findings:
                # Count licenses
                license_name = finding.get('name', 'NOASSERTION')  # Use 'NOASSERTION' for missing license data
                if license_name not in license_stats:
                    license_stats[license_name] = 0
                license_stats[license_name] += 1

                # Track how many findings have 'NOASSERTION' license
                if license_name == 'NOASSERTION':
                    no_assertion_count += 1

                # Count severity levels
                severity = finding.get('severity', '').upper()  # Make sure severity is in uppercase
                if severity in severity_stats:
                    severity_stats[severity] += 1
                else:
                    unknown_severity_count += 1  # Track unknown/missing severity values

                # Count package names
                package_name = finding.get('pkg_name', 'NOASSERTION')  # Use 'UNKNOWN_PACKAGE' for missing data
                if package_name not in package_stats:
                    package_stats[package_name] = 0
                package_stats[package_name] += 1
                total_packages += 1

            # Additional summary statistics
            license_count = sum(license_stats.values())  
            severity_count = sum(severity_stats.values())  
            unique_package_count = len(package_stats)  
            no_license_percentage = (no_assertion_count / license_count) * 100 if license_count > 0 else 0
            unknown_severity_percentage = (unknown_severity_count / len(findings)) * 100 if findings else 0

            # Prepare the response data
            response_data = {
                'findings': findings, 
                'license_stats': license_stats,  
                'severity_stats': severity_stats,  
                'package_stats': package_stats,  
                'summary_stats': {
                    'total_findings': len(findings),
                    'total_packages': total_packages,
                    'unique_package_count': unique_package_count,
                    'license_count': license_count,
                    'no_assertion_count': no_assertion_count,
                    'no_license_percentage': no_license_percentage,
                    'unknown_severity_count': unknown_severity_count,
                    'unknown_severity_percentage': unknown_severity_percentage,
                }
            }

            # Return results with statistical counts
            return {'success': 'Records fetched successfully', 'data': response_data}, '200 Ok'

        except Exception as e:
            return {'error': str(e)}, '500 Internal Server Error'

    def fetch_licenses_groupby_type_and_risk(self, request, fields):
        """
        Fetches all the licenses and SBOM objects by project id and grouping it by license type and risk level.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            # Extract project_id from fields
            project_id = fields.get('project_id')

            pipeline = [
                # Match the documents with the provided project_id
                {
                    '$match': {
                        'project_id': project_id  
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'pkg_name': '$pkg_name',
                            'category': '$category',
                            'severity': '$severity',
                        },
                        'total_count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {
                        '_id.pkg_name': 1  
                    }
                },
                # Optionally, add pagination here
                # { '$skip': 0 },
                # { '$limit': 100 }
            ]

            licenses_list = list(
                FindingLicense.objects.aggregate(pipeline)
            )
            
            return {'success': 'Records fetched successfully', 'data': licenses_list}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except Exception as e:
            print("Error: ", e)
            return {'error': 'Internal server error:' + str(e)}, '500 Internal Server Error'

        
    def fetch_sbom_vulnerabilities(self, request, fields):
        """
        Fetches all the vulnerabilities by project id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        project_id = fields.get('project_id', '')

        if not project_id:
            return {'error': 'Project ID is required'}, '400 Bad Request'

        try:
            # Create the aggregation pipeline
            pipeline = [
                {"$match": {
                    "project_id": project_id,
                    "$or": [
                        {"isdeleted": None}  
                    ]
                }},
                {"$sort": {"created": -1}},  
            ]

            # Execute the aggregation pipeline
            findings = list(FindingSBOMVulnerability.objects.aggregate(*pipeline))

            # If no records found, return an appropriate message
            if not findings:
                return {'error': 'No records found for the provided project_id'}, '200 Ok'
            
            # Return results with statistical counts
            return {'success': 'Records fetched successfully', 'data': findings}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except Exception as e:
            return {'error': str(e)}, '500 Internal Server Error'
        
            
    def fetch_licenses_by_project_id(self, request, fields):
        """
        Fetches a list of unique license names by project id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        project_id = fields.get('project_id', '')

        if not project_id:
            return {'error': 'Project ID is required'}, '400 Bad Request'

        try:
            # Create the aggregation pipeline
            pipeline = [
                {"$match": {
                    "project_id": project_id,
                    "$or": [
                        {"isdeleted": None},  
                        {"isdeleted": False}  
                    ]
                }},
                {"$group": {
                    "_id": "$name"  
                }},
                {"$project": {
                    "_id": 0,  
                    "name": "$_id"  
                }}
            ]

            # Execute the aggregation pipeline
            findings = list(FindingLicense.objects.aggregate(*pipeline))

            # If no records found, return an appropriate message
            if not findings:
                return {'error': 'No records found for the provided project_id'}, '200 Ok'
            
            # Extract the list of license names
            license_names = [item["name"] for item in findings]

            # Return results
            return {'success': 'Records fetched successfully', 'data': license_names}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except Exception as e:
            return {'error': str(e)}, '500 Internal Server Error'