from flask import jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import ManualComplianceEvaluation
from typing import List
from datetime import datetime, timezone
import uuid
import json


class ManualComplianceEvaluationController():
    """
    Defines Controller for Manual Compliance Evaluation
    """

    def __init__(self) -> None:
        pass

    def fetch_by_project_id(self, project_id) -> List[dict]:
        """
        Fetches Manual Compliance Evaluation by Project ID
        """
        # Validate JWT Token
        verify_jwt_in_request()
        try:
            pipeline = [
                {
                    "$match": {
                        "project_id": project_id
                    }
                },
                {
                    "$project": {
                        "isdeleted": 0
                    }
                }
            ]
            manual_compliance_evaluation = ManualComplianceEvaluation.objects.aggregate(
                *pipeline)
            return list(manual_compliance_evaluation)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    def add_entity(self, request) -> dict:
        """
        Adds or Updates a Manual Compliance Evaluation
        """
        # Validate JWT Token
        verify_jwt_in_request()
        try:
            request_json = request.get_json()
            if request_json is None:
                return jsonify({'error': 'Invalid Request'}), 400

            project_id = request_json.get('project_id')
            compliance_id = request_json.get('compliance_id')
            evaluation_status = request_json.get('evaluation_status')

            if not project_id or not compliance_id or evaluation_status is None:
                return jsonify({'error': 'Missing Project ID, Compliance ID, or Evaluation Status'}), 400

            # Check if the record exists
            existing_record = ManualComplianceEvaluation.objects(
                project_id=project_id,
                compliance_id=compliance_id
            ).first()

            if existing_record:
                # Update the existing record
                existing_record.evaluation_status = evaluation_status
                existing_record.updated = datetime.now(timezone.utc)
                existing_record.save()
                return jsonify({'message': 'Manual Compliance Evaluation updated successfully'}), 200
            else:
                # Create a new record
                manual_compliance_evaluation_obj = ManualComplianceEvaluation(
                    manual_compliance_evaluation_id=str(uuid.uuid4()),
                    compliance_id=compliance_id,
                    project_id=project_id,
                    evaluation_status=evaluation_status,
                    created=datetime.now(timezone.utc)
                )
                manual_compliance_evaluation_obj.save()
                return jsonify({'message': 'Manual Compliance Evaluation added successfully'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 400
