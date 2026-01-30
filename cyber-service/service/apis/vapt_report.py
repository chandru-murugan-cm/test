from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from controllers.VaptReportController import VaptReportController

vapt_report_blueprint = Blueprint('vapt_report_blueprint', __name__)
vapt_report_controller = VaptReportController()

@vapt_report_blueprint.route('/crscan/vapt-reports', methods=['POST'])
@jwt_required()
def upload_report():
    """
    API to upload a VAPT report.
    """
    if request.method == 'POST':
        return vapt_report_controller.upload_report(request)

@vapt_report_blueprint.route('/crscan/vapt-reports', methods=['GET'])
@jwt_required()
def get_reports():
    """
    API to get all VAPT reports for a project.
    """
    if request.method == 'GET':
        return vapt_report_controller.get_reports()

@vapt_report_blueprint.route('/crscan/vapt-reports/all-projects', methods=['GET'])
@jwt_required()
def get_all_projects():
    """
    API to get all projects for admin dropdown use.
    """
    return vapt_report_controller.get_all_projects()

@vapt_report_blueprint.route('/crscan/vapt-reports/all-users', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    API to get all users for admin dropdown use.
    """
    return vapt_report_controller.get_all_users()

@vapt_report_blueprint.route('/crscan/vapt-reports/user-projects/<target_user_id>', methods=['GET'])
@jwt_required()
def get_user_projects(target_user_id):
    """
    API to get projects created by a specific user. Admin only.
    """
    return vapt_report_controller.get_user_projects(target_user_id)

@vapt_report_blueprint.route('/crscan/vapt-reports/<vapt_report_id>/download', methods=['GET'])
@jwt_required()
def download_report(vapt_report_id):
    """
    API to download a VAPT report.
    """
    if request.method == 'GET':
        return vapt_report_controller.download_report(vapt_report_id)

@vapt_report_blueprint.route('/crscan/vapt-reports/<vapt_report_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_report(vapt_report_id):
    """
    API to update or delete a VAPT report.
    """
    if request.method == 'PUT':
        return vapt_report_controller.update_report(vapt_report_id)
    elif request.method == 'DELETE':
        return vapt_report_controller.delete_report(vapt_report_id)
