from controllers.util import *
from entities.CyberServiceEntity import Scheduler
from typing import List
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from mongoengine import *
from marshmallow import Schema, fields, ValidationError, INCLUDE
from datetime import datetime, timezone
import uuid
import json


class RefinedScanResultsControllerAddSchema(Schema):
    unformatted_scan_results_id = fields.String(required=True, error_messages={
        "required": "Unformatted Scan Results ID is required."})
    finding = fields.String(null=True, error_messages={
        "required": "Findings value is required."})
    target = fields.String(null=True, error_messages={
        "required": "Target value is required."})
    severity = fields.String(null=True, error_messages={
        "required": "Severity value is required."})
    severity_range = fields.String(null=True, error_messages={
        "required": "Severity range value is required."})
    scan_status = fields.String(null=True, error_messages={
        "required": "Scan Status value is required."})
    scanner = fields.String(null=True, error_messages={
        "required": "Scanner value is required."})
    scan_date = fields.String(null=True, error_messages={
        "required": "Scan date value is required."})


class RefinedScanResultsControllerUpdateSchema(Schema):
    _id = fields.String(required=True, error_messages={
        "required": "Refined Scan Results ID is required."})
    unformatted_scan_results_id = fields.String(required=True, error_messages={
        "required": "Unformatted Scan Results ID is required."})
    finding = fields.String(null=True, error_messages={
        "required": "Findings value is required."})
    target = fields.String(null=True, error_messages={
        "required": "Target value is required."})
    severity = fields.String(null=True, error_messages={
        "required": "Severity value is required."})
    severity_range = fields.String(null=True, error_messages={
        "required": "Severity range value is required."})
    scan_status = fields.String(null=True, error_messages={
        "required": "Status value is required."})
    scanner = fields.String(null=True, error_messages={
        "required": "Scanner value is required."})
    scan_date = fields.String(null=True, error_messages={
        "required": "Scan date value is required."})


class RefinedScanResultsController:
    """
    Defines controller methods for the Refined Scan Output entity.
    """

    def __init__(self) -> None:
        pass

    def _validateRefinedScanOutputAdd(self, request_json):
        schema = RefinedScanResultsControllerAddSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as e:
            return False, e.message, '400 Bad Request'
        return True, {'message': 'Validation successful'}, '200 Ok'

    def _validateRefinedScanOutputUpdate(self, request_json):
        schema = RefinedScanResultsControllerUpdateSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as e:
            return False, e.message, '400 Bad Request'
        return True, {'message': 'Validation Successful'}, '200 Ok'

    def _validateRefinedScanOutput(self, refined_scan_id):
        """"
        Validates the scan id with database
        """
        try:
            Refined_scan_results.objects.get(
                refined_scan_results_id=refined_scan_id)
            return True, {'message': 'Record exists in db'}, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the refined scan results objects from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            pipeline = [
                {
                    "$match": fields
                },
                {
                    "$lookup": {
                        "from": "Unformatted_scan_results",
                        "localField": "unformatted_scan_results_id",
                        "foreignField": "_id",
                        "as": "unformatted_scan_results_details"
                    }
                },
                {
                    "$project": {
                        "isdeleted": 0
                    }
                }
            ]

            # Execute the aggregation pipeline
            refined_scan_results_list = list(
                Refined_scan_results.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': refined_scan_results_list}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def update_by_id(self, request_json) -> dict:
        """"
        Updates the scan result object by id
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        request_json = request.get_json()
        status, result, status_code = self._validateRefinedScanOutputUpdate(
            request_json)
        if not status:
            return jsonify(result), status_code

        refined_scan_id = None
        if '_id' in request_json:
            refined_scan_id = request_json['_id']
            if request_json['_id'] is None or 0 == len(str(request_json['_id']).strip()):
                pass
            else:
                status, result, status_code = self._validateRefinedScanOutput(
                    request_json['_id'])
                if not status:
                    return result, status_code

        unformatted_scan_results_id = None
        if 'unformatted_scan_results_id' in request_json:
            unformatted_scan_results_id = request_json['unformatted_scan_results_id']

        finding = None
        if 'finding' in request_json:
            finding = request_json['finding']

        target = None
        if 'target' in request_json:
            target = request_json['target']

        severity = None
        if 'severity' in request_json:
            severity = request_json['severity']

        severity_range = None
        if 'severity_range' in request_json:
            severity_range = request_json['severity_range']

        scan_status = None
        if 'scan_status' in request_json:
            scan_status = request_json['scan_status']

        scanner = None
        if 'scanner' in request_json:
            scanner = request_json['scanner']

        scan_date = None
        if 'scan_date' in request_json:
            scan_date = request_json['scan_date']

        try:
            refined_scan_obj = Refined_scan_results.objects.get(
                refined_scan_results_id=refined_scan_id)
            refined_scan_obj['unformatted_scan_results_id'] = unformatted_scan_results_id
            refined_scan_obj['finding'] = finding
            refined_scan_obj['target'] = target
            refined_scan_obj['severity'] = severity
            refined_scan_obj['severity_range'] = severity_range
            refined_scan_obj['scan_status'] = scan_status
            refined_scan_obj['scanner'] = scanner
            refined_scan_obj['scan_date'] = scan_date
            refined_scan_obj['updator'] = current_user
            refined_scan_obj['updated'] = datetime.now(timezone.utc)
            refined_scan_obj.save()
            response = json.loads(refined_scan_obj.to_json())
            return {'success': 'Record updated successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def add_entity(self, request_json) -> dict:
        """
        Creates new scheduler obj in database
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        request_json = request.get_json()
        status, result, status_code = self._validateRefinedScanOutputAdd(
            request_json)
        if not status:
            return jsonify(result), status_code

        unformatted_scan_results_id = None
        if 'unformatted_scan_results_id' in request_json:
            unformatted_scan_results_id = request_json['unformatted_scan_results_id']

        finding = None
        if 'finding' in request_json:
            finding = request_json['finding']

        target = None
        if 'target' in request_json:
            target = request_json['target']

        severity = None
        if 'severity' in request_json:
            severity = request_json['severity']

        severity_range = None
        if 'severity_range' in request_json:
            severity_range = request_json['severity_range']

        scan_status = None
        if 'scan_status' in request_json:
            scan_status = request_json['scan_status']

        scanner = None
        if 'scanner' in request_json:
            scanner = request_json['scanner']

        scan_date = None
        if 'scan_date' in request_json:
            scan_date = request_json['scan_date']

        try:
            new_refined_scan_obj = Refined_scan_results(refined_scan_results_id=str(uuid.uuid4()),
                                                        unformatted_scan_results_id=unformatted_scan_results_id,
                                                        finding=finding,
                                                        target=target,
                                                        severity=severity,
                                                        severity_range=severity_range,
                                                        scan_status=scan_status,
                                                        scanner=scanner,
                                                        scan_date=scan_date,
                                                        created=datetime.now(
                timezone.utc),
                creator=current_user,
            )
            new_refined_scan_obj.save()
            response = json.loads(new_refined_scan_obj.to_json())
            return {'success': 'Record created successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def remove_entity(self, refined_scan_id):
        """
        Removes the Refined scan result object from the database.
        """
        # Validates the JWT Token
        verify_jwt_in_request()
        try:
            refined_scan_obj = Refined_scan_results.objects.get(
                refined_scan_results_id=refined_scan_id)
            refined_scan_obj.soft_delete()
            return {'success': 'Record Deleted Successfully'}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
