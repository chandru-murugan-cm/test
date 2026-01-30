import pytest
import io
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, JWTManager

from controllers.VaptReportController import VaptReportController
from entities.CyberServiceEntity import VaptReport, Project


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret"
    JWTManager(app)
    return app

@pytest.fixture
def controller():
    return VaptReportController()

def test_upload_report_admin_success(app, controller):
    with app.app_context():
        admin_token = create_access_token(identity='admin_user', additional_claims={'role': 'admin'})
        headers = {
            'Authorization': f'Bearer {admin_token}'
        }

        mock_file = MagicMock()
        mock_file.content_type = 'application/pdf'
        mock_file.filename = 'test_report.pdf'

        with app.test_request_context(method='POST', headers=headers, data={
            'project_id': 'test_project',
            'user_id': 'test_user',
            'year': '2023',
            'month': '10',
            'report_name': 'Test Report',
            'report_file': (io.BytesIO(b"abcdef"), 'test.pdf')
        }):
            with (patch('controllers.VaptReportController.get_jwt_identity') as mock_get_jwt_identity,
                patch('controllers.VaptReportController.get_jwt') as mock_get_jwt,
                patch('controllers.VaptReportController.Project.objects') as mock_project_objects,
                patch('controllers.VaptReportController.VaptReport') as mock_vapt_report):

                mock_get_jwt_identity.return_value = 'admin_user'
                mock_get_jwt.return_value = {'role': 'admin'}
                mock_project_objects.return_value.first.return_value = MagicMock()

                response, status_code = controller.upload_report(request)

                assert status_code == 201
                assert response['success'] == 'Report uploaded successfully'

def test_get_reports_user_success(app, controller):
    with app.app_context():
        user_token = create_access_token(identity='test_user', additional_claims={'role': 'user'})
        headers = {
            'Authorization': f'Bearer {user_token}'
        }

        with app.test_request_context(method='GET', headers=headers, query_string={
            'project_id': 'test_project',
            'user_id': 'test_user'
        }):
            with (patch('controllers.VaptReportController.get_jwt_identity') as mock_get_jwt_identity,
                patch('controllers.VaptReportController.get_jwt') as mock_get_jwt,
                patch('controllers.VaptReportController.VaptReport.objects') as mock_vapt_report_objects):

                mock_get_jwt_identity.return_value = 'test_user'
                mock_get_jwt.return_value = {'role': 'user'}

                mock_vapt_report_objects.return_value = [MagicMock()]

                response, status_code = controller.get_reports()

                assert status_code == 200
                assert response['success'] == 'Reports fetched successfully'
