from flask import request, jsonify
from mongoengine import *
from controllers.util import *
import uuid
from datetime import datetime, timezone
import json
from entities.CyberServiceEntity import RawScanOutput
from typing import List


class RawScanOutputController():
    """
    Defines controller methods for the Raw Scan Output Entity.
    """

    def __init__(self) -> None:
        pass

    def add_entity(self, request):
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        request_json = request.get_json()

        scanner_id = request_json.get('scanner_id')
        scan_id = request_json.get('scan_id')
        output = request_json.get('output')

        if not scanner_id:
            return jsonify({"error": "Scanner Id not provided"}), 400

        if not scan_id:
            return jsonify({"error": "Status not provided"}), 400
        
        if not output:
            return jsonify({"error": "Output not provided"}), 400

        # Creating the Raw Scan Output entry
        raw_scan_output_obj = RawScanOutput(
            raw_scan_output_id=str(uuid.uuid4()),
            scanner_id=scanner_id,
            scan_id=scan_id,
            output=output,
            created=datetime.now(timezone.utc),
            creator=current_user,
        )

        # Save the entity to the database
        raw_scan_output_obj.save()
        response = json.loads(raw_scan_output_obj.to_json())
        return jsonify({"message": "Raw Scan Output Entry created successfully", "data": response}), 201

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the raw scan output object from the database.
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        pipeline = [
            {
                "$match": {
                    **fields
                }
            },
            {
                "$project": {
                    "isdeleted": 0
                }
            }
        ]

        # Execute the aggregation pipeline
        raw_scan_output_list = list(RawScanOutput.objects.aggregate(pipeline))
        response = raw_scan_output_list
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'
