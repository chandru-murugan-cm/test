from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import jwt
from config_params import *


def get_current_user_from_jwt_token():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    return current_user

def get_decoded_token(request):
    token = request.headers.get("Authorization").split()[1]
    secret_key =JWTSECRET
    decoded_token = jwt.decode(token, key=secret_key, algorithms=["HS256"])
    return decoded_token