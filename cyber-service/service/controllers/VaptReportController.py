from flask import request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity, get_jwt
from mongoengine import ValidationError
from entities.CyberServiceEntity import VaptReport, Project
from bson import ObjectId
from datetime import datetime, timezone
from pymongo import MongoClient
from config_params import DATABASE_CONNECTION_STRING
import uuid
import io

def serialize_mongo_data(data):
    """
    Recursively converts ObjectId instances in MongoDB documents to strings.
    """
    if isinstance(data, dict):
        return {key: serialize_mongo_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data

class VaptReportController:
    """
    Controller to manage VaptReports.
    """

    def upload_report(self, request_data) -> dict:
        """
        Uploads a new VAPT report.
        """
        try:
            # Extract user_id from the JWT token
            uploaded_by = get_jwt_identity()
            if not uploaded_by:
                return {'error': 'User not authenticated'}, 401

            # Check for admin role
            claims = get_jwt()
            if not claims.get('role') == 'admin':
                return {'error': 'Unauthorized'}, 403

            project_id = request.form.get('project_id')
            user_id = request.form.get('user_id')
            year = request.form.get('year')
            month = request.form.get('month')
            report_name = request.form.get('report_name')
            report_file = request.files.get('report_file')

            if not all([project_id, user_id, year, month, report_name, report_file]):
                return {'error': 'Missing required fields'}, 400

            # Check if the project exists
            project = Project.objects(project_id=project_id).first()
            if not project:
                return {'error': 'Project not found'}, 404

            # Create a new VaptReport
            new_report = VaptReport(
                vapt_report_id=str(uuid.uuid4()),
                project_id=project_id,
                user_id=user_id,
                year=int(year),
                month=int(month),
                report_name=report_name,
                uploaded_at=datetime.now(timezone.utc),
                uploaded_by=uploaded_by
            )
            new_report.report_file.put(report_file, content_type=report_file.content_type, filename=report_file.filename)
            new_report.save()

            return {'success': 'Report uploaded successfully', 'data': serialize_mongo_data(new_report.to_mongo().to_dict())}, 201

        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, 400
        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500

    def get_reports(self) -> dict:
        """
        Retrieves all reports for a given project, user, year, and month.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {'error': 'User not authenticated'}, 401

            # Check for admin role
            claims = get_jwt()
            is_admin = claims.get('role') == 'admin'

            project_id = request.args.get('project_id')
            target_user_id = request.args.get('user_id')
            year = request.args.get('year')
            month = request.args.get('month')

            query = {}

            if project_id:
                query["project_id"] = project_id

            if not is_admin:
                # Non-admin users can only get their own reports
                query["user_id"] = user_id
            elif target_user_id:
                # Admin can filter by user_id
                query["user_id"] = target_user_id

            if year:
                query["year"] = int(year)
            if month:
                query["month"] = int(month)

            query["isdeleted__ne"] = True
            reports = VaptReport.objects(**query)

            serialized_reports = []
            for report in reports:
                report_data = serialize_mongo_data(report.to_mongo().to_dict())
                report_data.pop('report_file', None) # Exclude file content
                serialized_reports.append(report_data)

            return {'success': 'Reports fetched successfully', 'data': serialized_reports}, 200

        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500
            
    def download_report(self, vapt_report_id: str):
        """
        Downloads a VAPT report.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {'error': 'User not authenticated'}, 401

            report = VaptReport.objects(vapt_report_id=vapt_report_id).first()
            if not report:
                return {'error': 'Report not found'}, 404

            # Check if the user has access to the project associated with the report
            # or if the user is an admin
            claims = get_jwt()
            is_admin = claims.get('role') == 'admin'

            if not is_admin and report.user_id != user_id:
                 return {'error': 'Unauthorized'}, 403

            file_data = report.report_file.read()
            return send_file(
                io.BytesIO(file_data),
                mimetype=report.report_file.content_type,
                as_attachment=True,
                download_name=report.report_file.filename
            )

        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500

    def update_report(self, vapt_report_id: str) -> dict:
        """
        Updates an existing VAPT report (name, year, month, and optionally replaces the file).
        Admin only.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {'error': 'User not authenticated'}, 401

            claims = get_jwt()
            if not claims.get('role') == 'admin':
                return {'error': 'Unauthorized'}, 403

            report = VaptReport.objects(vapt_report_id=vapt_report_id, isdeleted__ne=True).first()
            if not report:
                return {'error': 'Report not found'}, 404

            report_name = request.form.get('report_name')
            year = request.form.get('year')
            month = request.form.get('month')
            report_file = request.files.get('report_file')

            if report_name:
                report.report_name = report_name
            if year:
                report.year = int(year)
            if month:
                report.month = int(month)

            if report_file:
                report.report_file.delete()
                report.report_file.put(report_file, content_type=report_file.content_type, filename=report_file.filename)

            report.save()

            report_data = serialize_mongo_data(report.to_mongo().to_dict())
            report_data.pop('report_file', None)
            return {'success': 'Report updated successfully', 'data': report_data}, 200

        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, 400
        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500

    def delete_report(self, vapt_report_id: str) -> dict:
        """
        Soft-deletes a VAPT report by setting isdeleted=True.
        Admin only.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {'error': 'User not authenticated'}, 401

            claims = get_jwt()
            if not claims.get('role') == 'admin':
                return {'error': 'Unauthorized'}, 403

            report = VaptReport.objects(vapt_report_id=vapt_report_id, isdeleted__ne=True).first()
            if not report:
                return {'error': 'Report not found'}, 404

            report.isdeleted = True
            report.save()

            return {'success': 'Report deleted successfully'}, 200

        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500

    def get_all_projects(self) -> dict:
        """
        Returns all non-deleted projects (id + name) for admin dropdown use.
        Bypasses the project controller's creator filter.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {'error': 'User not authenticated'}, 401

            claims = get_jwt()
            if not claims.get('role') == 'admin':
                return {'error': 'Unauthorized'}, 403

            projects = Project.objects(isdeleted__ne=True).only('project_id', 'name')
            data = []
            for p in projects:
                data.append({'_id': str(p.project_id), 'name': p.name})

            return {'success': 'Projects fetched successfully', 'data': data}, 200

        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500

    def get_user_projects(self, target_user_id) -> dict:
        """
        Returns non-deleted projects created by a specific user.
        Admin only.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {'error': 'User not authenticated'}, 401

            claims = get_jwt()
            if not claims.get('role') == 'admin':
                return {'error': 'Unauthorized'}, 403

            projects = Project.objects(creator=target_user_id, isdeleted__ne=True).only('project_id', 'name')
            data = []
            for p in projects:
                data.append({'_id': str(p.project_id), 'name': p.name})

            return {'success': 'Projects fetched successfully', 'data': data}, 200

        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500

    def get_all_users(self) -> dict:
        """
        Returns all users (id + name) from auth_db for admin dropdown use.
        Queries auth_db.users collection directly via PyMongo.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {'error': 'User not authenticated'}, 401

            claims = get_jwt()
            if not claims.get('role') == 'admin':
                return {'error': 'Unauthorized'}, 403

            client = MongoClient(DATABASE_CONNECTION_STRING)
            auth_db = client['auth_db']
            users_collection = auth_db['users']
            users = users_collection.find({}, {'_id': 1, 'fname': 1, 'lname': 1, 'email': 1})

            data = []
            for u in users:
                data.append({
                    '_id': str(u['_id']),
                    'fname': u.get('fname', ''),
                    'lname': u.get('lname', ''),
                    'email': u.get('email', ''),
                })

            return {'success': 'Users fetched successfully', 'data': data}, 200

        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500
