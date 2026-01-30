from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from controllers.SammUserScoreController import SammUserScoreController

samm_user_score_blueprint = Blueprint('samm_user_score_blueprint', __name__)
samm_user_score_controller = SammUserScoreController()

@samm_user_score_blueprint.route('/crscan/samm-scores', methods=['POST'])
@jwt_required()
def add_or_update_score():
    """
    API to add or update a SammUserScore.
    """
    if request.method == "POST":
        if request.data:
            return samm_user_score_controller.add_or_update_score(request)
        return {'error': 'Missing score details'}, 400

@samm_user_score_blueprint.route('/crscan/samm-scores', methods=['GET'])
@jwt_required()
def get_scores():
    """
    API to get scores for the authenticated user.
    """
    if request.method == "GET":
        return samm_user_score_controller.get_scores()
