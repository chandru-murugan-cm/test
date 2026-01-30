from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import RepositoryTrivy1
from typing import List


class RepositoryTrivy1Controller():
    """
    Defines controller methods for the Repository Trivy 1 Entity.
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches a Repository Trivy 1 object by its _id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "_id" in fields:
            repository_trivy_1_id = fields['_id']

            try:
                pipeline = [
                    {
                        "$match": {
                            "_id": repository_trivy_1_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0
                        }
                    }
                ]

                # Execute the aggregation pipeline
                repository_trivy_1_results_list = list(
                    RepositoryTrivy1.objects.aggregate(*pipeline)
                )

                return {'success': 'Records fetched successfully', 'data': repository_trivy_1_results_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
