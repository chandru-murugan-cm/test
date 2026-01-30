from flask import request, jsonify
from mongoengine import *
from controllers.util import *
import uuid
from datetime import datetime, timezone
import json
from entities.CyberServiceEntity import FindingScanLink
from typing import List


class FindingScanLinkController():
    """
    Defines controller methods for the Finding Scan Link Entity.
    """

    def __init__(self) -> None:
        pass

    def add_entity(self, request):
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        request_json = request.get_json()

        finding_id = request_json.get('finding_id')
        scan_id = request_json.get('scan_id')

        if not finding_id:
            return jsonify({"error": "Schedule Id not provided"}), 400

        if not scan_id:
            return jsonify({"error": "Status not provided"}), 400

        # Creating the Finding Scan Link entry
        finding_scan_link_obj = FindingScanLink(
            finding_scan_link_id=str(uuid.uuid4()),
            finding_id=finding_id,
            scan_id=scan_id,
            created=datetime.now(timezone.utc),
            creator=current_user,
        )

        # Save the entity to the database
        finding_scan_link_obj.save()
        response = json.loads(finding_scan_link_obj.to_json())
        return jsonify({"message": "Finding Scan Link Entry created successfully", "data": response}), 201

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the finding scan link object from the database.
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
        finding_scan_link_list = list(FindingScanLink.objects.aggregate(pipeline))
        response = finding_scan_link_list
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'
