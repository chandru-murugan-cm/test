from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import LanguagesAndFramework
from typing import List


class LanguagesAndFrameWorkController():
    """
    Defines controller methods for the Languages and Framework collection.
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches a Languages and Framework object by its project_id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "project_id" in fields:
            project_id = fields['project_id']

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

                # Execute the aggregation pipeline
                languages_and_framework_results_list = list(
                    LanguagesAndFramework.objects.aggregate(*pipeline)
                )

                return {'success': 'Records fetched successfully', 'data': languages_and_framework_results_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
