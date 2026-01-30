from flask import Flask
from config_params import *
from mongoengine import *
# from apis import api
from apis.scans import scans_blueprint
from apis.scanners import scanners_blueprint
from apis.project import project_blueprint
from apis.target_repo import repository_blueprint
from apis.target_domain import domain_blueprint
from apis.scheduler import scheduler_blueprint
from apis.unformatted_scan_results import unformatted_scan_results_blueprint
from apis.refined_scan_results import refined_scan_results_blueprint
from apis.scanner_types import scanner_type_blueprint
from apis.finding_scan_link import finding_scan_link_blueprint
from apis.repo_scan_results import repo_scan_results_blueprint
from apis.finding_master import finding_master_blueprint
from apis.domain_wapiti_1 import domain_wapiti_1_blueprint
from apis.domain_zap_1 import domain_zap_1_blueprint
from apis.repository_trivy_1 import repository_trivy_1_blueprint
from apis.fix_recomendation import fix_recomendation_blueprint
from apis.languages_and_framework import languages_and_framework_blueprint
from apis.target_contract import contract_blueprint
from flask_cors import CORS
from apis.compliance import compliance_blueprint
from apis.samm import samm_blueprint
from apis.github_oauth import github_oauth_blueprint
from apis.target_azure_cloud import target_azure_cloud_blueprint
from apis.target_google_cloud import target_google_cloud_blueprint
from apis.asvs import asvs_blueprint
from apis.samm_user_score_api import samm_user_score_blueprint
from apis.compliance_scanner_mapping import compliance_scanner_mapping_blueprint
from apis.framework_scanner_mapping import framework_scanner_mapping_blueprint
from apis.manual_compliance_evaluation import manual_compliance_evaluation_blueprint
from apis.owasp_top_ten import owasp_top_ten_blueprint
from apis.asvs_scanner_mapping import asvs_scanner_mapping_blueprint
from apis.owasptopten_scanner_mapping import owasptopten_scanner_mapping_blueprint
from apis.vapt_report import vapt_report_blueprint
from apis.manual_vapt_upload import manual_vapt_upload_blueprint
from docs.swagger.swagger_config import init_swagger

app = Flask(__name__)

# Set the secret key for session management
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_default_secret_key")  # Load from env or set a default key
app.secret_key = "myownsecret"  

CORS(app)


# # api.init_app(app, debug=True)
from flask_jwt_extended import JWTManager
app.config["JWT_SECRET_KEY"] = 'myownsecret'
jwt = JWTManager(app)

app.register_blueprint(scans_blueprint)
app.register_blueprint(scanners_blueprint)
app.register_blueprint(scanner_type_blueprint)
app.register_blueprint(project_blueprint)
app.register_blueprint(scheduler_blueprint)
app.register_blueprint(repository_blueprint)
app.register_blueprint(domain_blueprint)
app.register_blueprint(finding_master_blueprint)
app.register_blueprint(domain_wapiti_1_blueprint)
app.register_blueprint(repository_trivy_1_blueprint)
app.register_blueprint(domain_zap_1_blueprint)
app.register_blueprint(refined_scan_results_blueprint)
app.register_blueprint(finding_scan_link_blueprint)
app.register_blueprint(repo_scan_results_blueprint)
app.register_blueprint(fix_recomendation_blueprint)
app.register_blueprint(languages_and_framework_blueprint)
app.register_blueprint(contract_blueprint)
app.register_blueprint(compliance_blueprint)
app.register_blueprint(samm_blueprint)
app.register_blueprint(github_oauth_blueprint)
app.register_blueprint(target_azure_cloud_blueprint)
app.register_blueprint(target_google_cloud_blueprint)
app.register_blueprint(asvs_blueprint)
app.register_blueprint(samm_user_score_blueprint)
app.register_blueprint(compliance_scanner_mapping_blueprint)
app.register_blueprint(framework_scanner_mapping_blueprint)
app.register_blueprint(manual_compliance_evaluation_blueprint)
app.register_blueprint(owasp_top_ten_blueprint)
app.register_blueprint(asvs_scanner_mapping_blueprint)
app.register_blueprint(owasptopten_scanner_mapping_blueprint)
app.register_blueprint(vapt_report_blueprint)
app.register_blueprint(manual_vapt_upload_blueprint)

from pymongo import MongoClient
client = MongoClient(DATABASE_CONNECTION_STRING)
db = client[DATABASE_NAME]
from mongoengine import register_connection
register_connection(alias='default', name=DATABASE_NAME, host=DATABASE_CONNECTION_STRING)

# Initialize Swagger documentation
swagger = init_swagger(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")

# START DATABASE ORM CONFIGURATION
# connect(db=DATABASE_NAME, host=MONGODBDSN, ssl=True, ssl_cert_reqs=None)
# connect(db='cyber-service_1', host="mongodb://localhost:27017/")
# # END DATABASE ORM CONFIGURATION
