from mongoengine import *
from enum import Enum
from mongoengine_softdelete.document import SoftDeleteNoCacheDocument

class SchedulerType(Enum):
    Daily = 'daily'
    Monthly = 'monthly'
    Weekly = 'weekly'
    Custom = 'custom'
    ScanNow = 'scanNow'


class ProjectStatus(Enum):
    Init = 'init'
    Pending = 'pending'
    Completed = 'completed'

class ScanTargetType(Enum):
    REPO = 'repo'
    DOMAIN = 'domain'
    CONTAINER = 'container'
    CLOUD = 'cloud'
    WEB3 = 'web3'
    VM = 'vm'

class ScanStatus(Enum):
    Scheduled = 'scheduled'
    Running = 'running'
    Completed = 'completed'
    Error = 'error'

class FindingStatus(Enum):
    Open = 'open'
    Closed = 'closed'
    Ignored = 'ignored'
    FalsePositive = 'false positive'

class FindingSeverity(Enum):
    Critical = 'critical'
    High = 'high'
    Medium = 'medium'
    Low = 'low'
    Informational = 'informational'

class CloudPurposeType(Enum):
    Development = 'development'
    Staging = 'staging'
    Production = 'production'

class Scanners(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'Scanners',
        'soft_delete': {'isdeleted': True},
        'indexes': ['name'],
        'strict': False
    }
    # pk, fk
    scanner_id = StringField(required=True, primary_key=True)

    # Business Fields
    name = StringField(required=True)
    description = StringField(null=False, max_length=255)
    version = StringField(null=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)

class ScannerTypes(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'ScannerTypes',
        'soft_delete': {'isdeleted': True},
        'indexes': ['scan_type'],
        'strict': False
    }

    # pk, fk
    scan_type_id = StringField(required=True, primary_key=True)
    scanner_ids = ListField(StringField(), required=True)

    # Business Fields
    scan_type = StringField(required=True)
    scan_target_type = EnumField(ScanTargetType, null=True)
    cloud_provider = StringField(null=True)  # New field for GCP/Azure
    description = StringField(null=False)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    isdeleted = BooleanField(default=False, null=True)


class Scheduler(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'Scheduler',
        'soft_delete': {'isdeleted': True},
        'indexes': ['options'],
        'strict': False
    }
    # pk, fk
    scheduler_id = StringField(required=True, primary_key=True)
    project_id = StringField(null=True)
    # scanner_id = StringField(null=True)
    # Business Fields
    options = EnumField(SchedulerType, required=True)
    scanner_type_ids_list = ListField(StringField(), null=True)
    # scanner_names_list = ListField(StringField(), null=True)
    schedule_date = DateTimeField(null=True)
    day = StringField(null=True)  # Day for weekly schedules
    date = IntField(null=True)  # Date for monthly schedules (1-31)
    time = StringField(null=True)
    status = StringField(required=True)
    next_run = DateTimeField(null=True)
    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)


class Project(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'Project',
        'soft_delete': {'isdeleted': True},
        'indexes': ['name'],
        'strict': False
    }
    # pk, fk
    project_id = StringField(required=True, primary_key=True)
    user_id = StringField(null=True)
    # Business Fields
    organization = StringField(required=True)
    status = EnumField(ProjectStatus, null=True)
    name = StringField(required=True, max_length=75)
    description  = StringField(null=True)
    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)

class Repository(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'TargetRepository',
        'soft_delete': {'isdeleted': True},
        'indexes': ['repository_url', 'project_id'],
        'strict': False
    }
    # pk, fk
    target_repository_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)

    # Business Fields
    repository_url = StringField(required=True)
    repository_label = StringField(null=True)
    is_private_repo = BooleanField(default=False, null=True)
    access_token = StringField(null=True)
    repository_provider = StringField(required=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)

class Domain(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'TargetDomain',
        'soft_delete': {'isdeleted': True},
        'indexes': ['domain_url', 'project_id'],
        'strict': False
    }
    # pk, fk
    target_domain_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)

    # Business Fields
    domain_url = StringField(required=True)
    domain_label = StringField(null=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)

class FileEntry(EmbeddedDocument):
    """
    Represents an individual file uploaded for the contract.
    """
    file_id = FileField(required=True)
    file_name = StringField(required=True)
    file_content = StringField(required=True)
    file_path = StringField(null=True)
    created = DateTimeField(null=True)


class Contract(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'TargetContract',
        'soft_delete': {'isdeleted': True},
        'indexes': ['contract_url', 'project_id'],
        'strict': False
    }

    # Primary and Foreign Keys
    target_contract_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)

    # Business Fields
    contract_url = StringField(null=True)
    contract_label = StringField(null=True)

    # Solidity File Upload Fields (Allowing multiple files)
    solidity_files = EmbeddedDocumentListField(FileEntry, default=list)  # List of uploaded files

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete Field
    isdeleted = BooleanField(default=False, null=True)


class Scans(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'Scans',
        'soft_delete': {'isdeleted': True},
        'indexes': ['status'],
        'strict': False
    }
    # pk, fk
    scan_id = StringField(required=True, primary_key=True)
    scheduler_id = StringField(required=True)
    project_id = StringField(required=True)

    # Business Fields
    status = EnumField(ScanStatus, required=True)
    execution_date = DateTimeField(null=True)
    duration = StringField(null=True)
    description = StringField(null=True)
    

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)


class FindingMaster(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'FindingMaster',
        'soft_delete': {'isdeleted': True},
        'indexes': ['finding_name'],
        'strict': False
    }
    # pk, fk
    finding_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)
    target_id = StringField(required=True)
    scan_type_id = StringField(required=True)
    extended_finding_details_name = StringField(null=True)
    extended_finding_details_id = StringField(null=True)
    fix_recommendation_id = StringField(null=True)
    raw_scan_output_id = StringField(required=True)

    # Business Fields
    finding_name = StringField(null=True)
    finding_desc = StringField(null=False)
    finding_date = DateTimeField(null=True)
    severity = EnumField(FindingSeverity, null=True)
    status = EnumField(FindingStatus, null=True)
    target_type = EnumField(ScanTargetType, null=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)


class FindingScanLink(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'FindingScanLink',
        'soft_delete': {'isdeleted': True},
        'indexes': ['scan_id'],
        'strict': False
    }
    # pk, fk
    finding_scan_link_id = StringField(required=True, primary_key=True)
    finding_id = StringField(required=True)
    scan_id = StringField(required=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)

class RawScanOutput(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'RawScanOutput',
        'soft_delete': {'isdeleted': True},
        'indexes': ['output'],
        'strict': False
    }
    # pk, fk
    raw_scan_output_id = StringField(required=True, primary_key=True)
    scan_id = StringField(required=True)
    scanner_id = StringField(required=True)

    # Business Fields
    output = StringField(null=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)


class DomainZap1(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'DomainZap1',
        'soft_delete': {'isdeleted': True},
        'indexes': ['alert'],
        'strict': False
    }
    
    # pk, fk
    domain_zap_1_id = StringField(required=True, primary_key=True)  

    # Business Fields
    param = StringField(null=True)  
    attack = StringField(null=True)  
    reference = StringField(null=True)  
    confidence = StringField(null=True)  
    cweid = StringField(null=True)  
    wascid = StringField(null=True)  
    evidence = StringField(null=True)  
    method = StringField(null=True)  
    other = StringField(null=True)  
    alert = StringField(null=True)  

    # System Fields
    created = DateTimeField(null=True)  
    updated = DateTimeField(null=True)  
    creator = StringField(null=True)  
    updator = StringField(null=True)  

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)

class FindingLicensesAndSbom(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'FindingLicensesAndSbom',
        'soft_delete': {'isdeleted': True},
        'indexes': ['pkgname'],
        'strict': False,
    }
    # pk, fk
    finding_licenses_and_sbom_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)
    scan_type_id = StringField(required=True)
    target_id = StringField(required=True)
    fix_recommendation_id = StringField(null=True)
    # Business fields
    finding_date = DateTimeField(required=True)
    severity = StringField(null=True)
    category = StringField(null=True)
    pkgname = StringField(null=True)
    filepath = StringField(null=True)
    name = StringField(null=True)
    text = StringField(null=True)
    link = StringField(null=True)
    target_type = EnumField(ScanTargetType, null=True)
    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)  


class FixRecommendations(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'FixRecommendations',
        'soft_delete': {'isdeleted': True},
        'indexes': ['scanner_fix'],
        'strict': False
    }
    
    # pk, fk
    fix_recommendation_id = StringField(required=True, primary_key=True)  

    # Business Fields
    scanner_fix = StringField(null=True)  
    ai_fix = StringField(null=True)  

    # System Fields
    created = DateTimeField(null=True)  
    updated = DateTimeField(null=True)  
    creator = StringField(null=True)  
    updator = StringField(null=True)  

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)  
    
    
class DomainWapiti1(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'DomainWapiti1',
        'soft_delete': {'isdeleted': True},
        'indexes': ['url'],
        'strict': False
    }

    # pk, fk
    domain_wapiti_1_id = StringField(required=True, primary_key=True)

    # Business Fields
    url = StringField(null=True)  
    vulnerability_type = StringField(null=True)  
    alert = StringField(null=True)  
    affected_parameters = ListField(StringField(), null=True)
    http_method = StringField(null=True)  
    payload = StringField(null=True)  
    evidence = StringField(null=True)  
    cwe_id = StringField(null=True)  
    references = StringField(null=True)  
    http_request = StringField(null=True)  
    curl_command = StringField(null=True)  
    module = StringField(null=True)  

    # System Fields
    created = DateTimeField(null=True)  
    updated = DateTimeField(null=True)  
    creator = StringField(null=True)  
    updator = StringField(null=True)  

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)

class RepoSecretDetections(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'RepoSecretDetections',
        'soft_delete': {'isdeleted': True},
        'indexes': ['file_name'],
        'strict': False
    }
    # pk, fk
    repo_secret_detections_id = StringField(required=True, primary_key=True)  
    # Business Fields
    secret = StringField(null=True)  
    cweid = StringField(null=True)  
    wascid = StringField(null=True)  
    file_name = StringField(null=True)
    line_number = StringField(null=True)
    column_number = StringField(null=True)
    fix_time = StringField(null=True)
    references = ListField(StringField(), null=True)
    # System Fields
    created = DateTimeField(null=True)  
    updated = DateTimeField(null=True)  
    creator = StringField(null=True)
    updator = StringField(null=True)
    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)

class RepositoryTrivy1(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'RepositoryTrivy1',
        'soft_delete': {'isdeleted': True},
        'indexes': ['uri'],
        'strict': False
    }

    # pk, fk
    repository_trivy_1_id = StringField(required=True, primary_key=True)

    # Business Fields
    finding_id = StringField(required=True)
    alert = StringField(null=True)
    uri = StringField(null=True)
    param = StringField(null=True)
    evidence = StringField(null=True)
    otherinfo = StringField(null=True)
    cweid = ListField(StringField(), null=True)
    target_host = StringField(null=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)

class LanguagesAndFramework(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'LanguagesAndFramework',
        'soft_delete': {'isdeleted': True},
        'indexes': ['project_id'],
        'strict': False
    }

    languages_and_framework_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)
    raw_scan_output_id = StringField(null=True)
    finding_date = DateTimeField(required=True)
    target_id = StringField(null=True)
    scan_type_id = StringField(null=True)
    language_name = StringField(null=True)
    language_count = IntField(null=True)
    language_percentage = FloatField(null=True)

    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    isdeleted = BooleanField(default=False, null=True)

class Compliance(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'Compliance',
        'soft_delete': {'isdeleted': True},
        'indexes': ['compliance_type'],
        'strict': False
    }
    compliance_id = StringField(required=True, primary_key=True)

    compliance_type = StringField(required=True)
    compliance_control_name = StringField(required=True)
    compliance_group_name = StringField(required=True)
    affecting_scan_type_id = StringField()
    compliance_subset_name = StringField(null=False) 


    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    isdeleted = BooleanField(default=False, null=True)

class RepoSmartContractSlither1(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'RepoSmartContractSlither1',
        'soft_delete': {'isdeleted': True},
        'indexes': ['contract'],
        'strict': False
    }

    repo_smart_contract_slither_1_id = StringField(required=True, primary_key=True)
    issue_type = StringField(null=True)
    line_number = StringField(null=True)
    contract = StringField(null=True)
    function = StringField(null=True)
    source_code_snippet = StringField(null=True)
    cwe_id = StringField(null=True)
    references = StringField(null=True)

    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    isdeleted = BooleanField(default=False, null=True)

class CoverageItem(EmbeddedDocument):
    coverage_name = StringField(required=True)  # Field for the coverage name
    coverage_description = StringField(required=True)  # Field for the description
    coverage_score = FloatField(required=True) 

class Samm(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'Samm',
        'soft_delete': {'isdeleted': True},
        'indexes': ['l1_business_function'],
        'strict': False
    }
    samm_id = StringField(required=True, primary_key=True)

    l1_business_function = StringField(null=True)
    l2_security_practice = StringField(null=True)
    l3_stream = StringField(null=True)
    l4_strategy_and_metrics = StringField(null=True)
    l4_strategy_and_metrics_question = StringField(null=True)
    l4_strategy_and_metrics_description = StringField(null=True)
    l4_strategy_and_metrics_coverage = ListField(EmbeddedDocumentField(CoverageItem), null=True)

    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    isdeleted = BooleanField(default=False, null=True)

class OwaspTopTen(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'OwaspTopTen',
        'soft_delete': {'isdeleted': True},
        'indexes': ['control_name'],
        'strict': False
    }
    owasp_top_ten_id = StringField(required=True, primary_key=True)

    control_name = StringField(null=True)
    group_name = StringField(null=True)

    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    isdeleted = BooleanField(default=False, null=True)


class SammUserScore(Document):
    meta = {
        'collection': 'SammUserScores',
        'soft_delete': {'isdeleted': True},
        'indexes': ['samm_id'],
        'strict': False
        }

    user_id = StringField(required=True)
    project_id = StringField(required=True)
    samm_id = StringField(required=True)
    score = FloatField(required=True, min_value=0.0)  
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)
    isdeleted = BooleanField(default=False)
    
class TargetAzureCloud(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'TargetAzureCloud',
        'soft_delete': {'isdeleted': True},
        'indexes': ['project_id'],
        'strict': False
    }
    azure_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)

    application_id = StringField(null=True)
    directory_id = StringField(null=True)
    client_secret_key = StringField(null=True)
    subscription_id = StringField(null=True)
    name = StringField(null=True)

    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    isdeleted = BooleanField(default=False, null=True)
    
class TargetGoogleCloud(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'TargetGoogleCloud',
        'soft_delete': {'isdeleted': True},
        'indexes': ['project_id'],
        'strict': False
    }
    google_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)

    name = StringField(null=True)
    type = StringField(null=True)
    gcp_project_id = StringField(null=True)
    private_key_id = StringField(null=True)
    private_key = StringField(null=True)
    client_email = StringField(null=True)
    client_id = StringField(null=True)
    auth_uri = StringField(null=True)
    token_uri = StringField(null=True)
    auth_provider_x509_cert_url = StringField(null=True)
    client_x509_cert_url = StringField(null=True)
    universe_domain = StringField(null=True)

    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    isdeleted = BooleanField(default=False, null=True)
    
class CloudCloudSploitAzure1(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'CloudCloudSploitAzure1',
        'soft_delete': {'isdeleted': True},
        'indexes': ['category'],
        'strict': False
    }

    # pk, fk
    cloud_azure_id = StringField(required=True, primary_key=True)

    # Business Fields
    plugin = StringField(null=True)
    category = StringField(null=True)
    description = StringField(null=True)
    resource = StringField(null=True)
    region = StringField(null=True)
    status = StringField(null=True)
    message = StringField(null=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)
    
class CloudCloudSploitGoogle1(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'CloudCloudSploitGoogle1',
        'soft_delete': {'isdeleted': True},
        'indexes': ['category'],
        'strict': False
    }

    # pk, fk
    cloud_google_id = StringField(required=True, primary_key=True)

    # Business Fields
    plugin = StringField(null=True)
    category = StringField(null=True)
    title = StringField(null=True)
    description = StringField(null=True)
    resource = StringField(null=True)
    region = StringField(null=True)
    status = StringField(null=True)
    message = StringField(null=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)
    
class AsvsRequirement(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'AsvsRequirement',
        'soft_delete': {'isdeleted': True},
        'indexes': ['chapter_id', 'section_id', 'requirement_id'],  # Indexes for optimized querying
        'strict': False
    }
    asvs_id = StringField(required=True, primary_key=True) # Unique primary key
    requirement_id = StringField(required=True)  
    chapter_id = StringField(null=True)  # Example: "V1"
    chapter_name = StringField(null=True)  # Example: "Architecture, Design and Threat Modeling"
    section_id = StringField(null=True)  # Example: "V1.1"
    section_name = StringField(null=True)  # Example: "Secure Software Development Lifecycle"
    requirement_name = StringField(null=True)  # Example: Detailed description
    requirement_reference = URLField(null=True)  # URL for references

    created = DateTimeField(null=True)  # Timestamp for creation
    updated = DateTimeField(null=True)  # Timestamp for updates
    creator = StringField(null=True)  # Creator's name or ID
    updator = StringField(null=True)  # Updator's name or ID

    isdeleted = BooleanField(default=False, null=True)  # Soft delete field

class ComplianceScannerMapping(Document):
    meta = {
        'collection': 'ComplianceScannerMapping',
        'soft_delete': {'isdeleted': True},
        'indexes': ['scanner_type_id'],
        'strict': False
    }
    # pk, fk
    compliance_scanner_mapping_id = StringField(required=True, primary_key=True)

    # Business Fields
    scanner_type_id = ListField(StringField(), required=True)
    compliance_id = StringField(required=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)
class OwaspTopTenScannerMapping(Document):
    meta = {
        'collection': 'OwaspTopTenScannerMapping',
        'soft_delete': {'isdeleted': True},
        'indexes': ['scanner_type_id'],
        'strict': False
    }
    # pk, fk
    owasptopten_scanner_mapping_id = StringField(required=True, primary_key=True)

    # Business Fields
    scanner_type_id = ListField(StringField(),default=[], required=True)
    owasp_top_ten_id = StringField(required=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)

class AsvsScannerMapping(Document):
    meta = {
        'collection': 'AsvsScannerMapping',
        'soft_delete': {'isdeleted': True},
        'indexes': ['scanner_type_id'],
        'strict': False
    }
    # pk, fk
    asvs_scanner_mapping_id = StringField(required=True, primary_key=True)

    # Business Fields
    scanner_type_id = ListField(StringField(),default=[],required=True)
    asvs_id = StringField(required=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)

class FrameworkScannerMapping(Document):
    meta = {
        'collection': 'FrameworkScannerMapping',
        'soft_delete': {'isdeleted': True},
        'indexes': ['scanner_type_id'],
        'strict': False
    }
    # pk, fk
    framework_scanner_mapping_id = StringField(required=True, primary_key=True)

    # Business Fields
    scanner_type_id = ListField(StringField(),default=[], required=True)
    framework_id = StringField(required=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)

class ManualComplianceEvaluation(Document):
    meta = {
        'collection': 'ManualComplianceEvaluation',
        'soft_delete': {'isdeleted': True},
        'indexes': ['project_id', 'compliance_id'],
        'strict': False
    }

    # pk, fk
    manual_compliance_evaluation_id = StringField(required=True, primary_key=True)

    # Business Fields
    project_id = StringField(required=True)
    compliance_id = StringField(required=True)
    evaluation_status = StringField(required=True)

    # System Fields
    created = DateTimeField(null=True)
    updated = DateTimeField(null=True)
    creator = StringField(null=True)
    updator = StringField(null=True)

    # Soft Delete
    isdeleted = BooleanField(default=False, null=True)


class FindingSBOMVulnerability(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'FindingSBOMVulnerability',
        'soft_delete': {'isdeleted': True},
        'indexes': ['vulnerabilityid'],
        'strict': False
    }

    # pk, fk
    sbom_vulnerability_id = StringField(required=True, primary_key=True)
    project_id = StringField(null=True)
    scan_type_id = StringField(null=True)
    target_id = StringField(null=True)
    target_type = StringField(null=True)

    # Business Fields
    vulnerabilityid = StringField(null=True)
    pkgid = StringField(null=True)
    pkg_name = StringField(null=True)
    pkg_identifier = DictField(null=True)
    installed_version = StringField(null=True)
    fixed_version = StringField(null=True)
    status = StringField(null=True)
    severity_source = StringField(null=True)
    primary_url = StringField(null=True)
    data_source = DictField(null=True)
    title = StringField(null=True)
    severity = StringField(null=True)
    description = StringField(null=True)
    vendor_severity = DictField(null=True)
    references = StringField(null=True)

    # System Fields
    created = DateTimeField(required=True)
    updated = DateTimeField(null=True)
    creator = StringField(required=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)

class FindingLicense(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'FindingLicense',
        'soft_delete': {'isdeleted': True},
        'indexes': ['pkg_name'],
        'strict': False
    }

    # pk, fk
    license_id = StringField(required=True, primary_key=True)
    project_id = StringField(null=True)
    scan_type_id = StringField(null=True)
    target_id = StringField(null=True)
    target_type = StringField(null=True)

    # Business Fields
    severity = StringField(null=True)
    category = StringField(null=True)
    pkg_name = StringField(null=True)
    file_path = StringField(null=True)
    name = StringField(null=True)
    text = StringField(null=True)
    link = StringField(null=True)

    # System Fields
    created = DateTimeField(required=True)
    updated = DateTimeField(null=True)
    creator = StringField(required=True)
    updator = StringField(null=True)

    # Declare the field used to check if the record is soft deleted
    # this field must also be reported in the `meta['soft_delete']` dict
    isdeleted = BooleanField(default=False, null=True)

class VaptReport(SoftDeleteNoCacheDocument, Document):
    meta = {
        'collection': 'VaptReport',
        'soft_delete': {'isdeleted': True},
        'indexes': ['project_id', 'user_id', 'year', 'month'],
        'strict': False
    }
    vapt_report_id = StringField(required=True, primary_key=True)
    project_id = StringField(required=True)
    user_id = StringField(required=True)
    year = IntField(required=True)
    month = IntField(required=True)
    report_name = StringField(required=True)
    report_file = FileField()
    uploaded_at = DateTimeField(required=True)
    uploaded_by = StringField(required=True)
    isdeleted = BooleanField(default=False, null=True)
