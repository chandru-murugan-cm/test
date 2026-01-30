from flask import request, Blueprint
import urllib.parse
from controllers.ManualComplianceEvaluationController import ManualComplianceEvaluationController

manual_compliance_evaluation_blueprint = Blueprint(
    'manual_compliance_evaluation_blueprint', __name__)
manual_compliance_evaluation_controller = ManualComplianceEvaluationController()


@manual_compliance_evaluation_blueprint.route('/crscan/manual_compliance_evaluation', methods=['GET'])
def get_manual_compliance_evaluation():
    """
    Fetch the manual compliance evaluation by _id, compliance_id using query parameters.
    """
    project_id = urllib.parse.unquote(request.args.get('project_id', ''))
    if project_id:
        return manual_compliance_evaluation_controller.fetch_by_project_id(project_id)
    return {'error': 'No valid query parameter provided'}, '400 Bad Request'


@manual_compliance_evaluation_blueprint.route('/crscan/manual_compliance_evaluation', methods=['POST'])
def create_manual_compliance_evaluation():
    """
    Create a new manual compliance evaluation.
    """
    if request.method == "POST":
        if request.data:
            return manual_compliance_evaluation_controller.add_entity(request)
        return {'error': 'Missing Manual Compliance Evaluation details'}, '400 Bad Request'

    return {'error': 'Invalid request'}, '400 Bad Request'
