from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from mongoengine import ValidationError
from entities.CyberServiceEntity import SammUserScore
from bson import ObjectId
from datetime import datetime, timezone

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

class SammUserScoreController:
    """
    Controller to manage SammUserScores.
    """

    def add_or_update_score(self, request_data) -> dict:
        """
        Adds or updates a score for a user and samm combination.
        """
        try:
            # Extract user_id from the JWT token
            user_id = get_jwt_identity()
           
            if not user_id:
                return {'error': 'User not authenticated'}, 401

            request_json = request_data.get_json()
            

            # Validate required fields
            if not request_json.get('samm_id') or not request_json.get('score') or not request_json.get('project_id'):
                return {'error': 'samm_id, score, and project_id are required'}, 400

            # Check if a score already exists for the user, samm, and project
            existing_score = SammUserScore.objects(
                user_id=user_id,
                samm_id=request_json['samm_id'],
                project_id=request_json['project_id'],
                isdeleted=False
            ).first()

            if existing_score:
                # Update the score if it exists
                existing_score.score = request_json['score']
                existing_score.updated = datetime.now(timezone.utc)
                existing_score.updator=user_id
                existing_score.save()
                return {'success': 'Score updated successfully', 'data': serialize_mongo_data(existing_score.to_mongo().to_dict())}, 200
            else:
                # Create a new score if it doesn't exist
                new_score = SammUserScore(
                    user_id=user_id,
                    samm_id=request_json['samm_id'],
                    project_id=request_json['project_id'],
                    score=request_json['score'],
                    created=datetime.now(timezone.utc),
                    creator=user_id,
                )
                new_score.save()
                return {'success': 'Score added successfully', 'data': serialize_mongo_data(new_score.to_mongo().to_dict())}, 201

        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, 400
        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500

    def get_scores(self) -> dict:
        """
        Retrieves all scores for the authenticated user filtered by project_id.
        """
        try:
            # Extract user_id from the JWT token
            user_id = get_jwt_identity()

            if not user_id:
                return {'error': 'User not authenticated'}, 401

            # Extract project_id from query params
            project_id = request.args.get('project_id')

            if not project_id:
                return {'error': 'project_id is required'}, 400

            scores = SammUserScore.objects(user_id=user_id, project_id=project_id, isdeleted=False)

            # Serialize the scores
            serialized_scores = [serialize_mongo_data(score.to_mongo().to_dict()) for score in scores]

            return {
                'success': 'Scores fetched successfully',
                'data': serialized_scores if scores else [],
                'message': 'No scores found for the specified project' if not scores else None
            }, 200

        except Exception as e:
            return {'error': 'An error occurred: ' + str(e)}, 500

