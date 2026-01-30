from flask import Blueprint, request, redirect, session, jsonify
import os
import requests
import urllib.parse
from dotenv import load_dotenv
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response

# Load environment variables from .env file
load_dotenv()

# GitHub OAuth Config
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

# Create a blueprint for GitHub OAuth
github_oauth_blueprint = Blueprint('github_oauth_blueprint', __name__)

# Step 1: Redirect user to GitHub OAuth login page
@github_oauth_blueprint.route('/auth/github', methods=['GET'])
@swag_from({
    'tags': ['OAuth'],
    'summary': 'Initiate GitHub OAuth authentication',
    'description': 'Redirect user to GitHub OAuth authorization page to grant repository access permissions',
    'responses': {
        302: {
            'description': 'Redirect to GitHub OAuth authorization page',
            'headers': {
                'Location': {
                    'type': 'string',
                    'description': 'GitHub OAuth authorization URL'
                }
            }
        },
        500: {
            'description': 'OAuth configuration error',
            'schema': error_response
        }
    }
})
def github_login():
    github_authorize_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(GITHUB_REDIRECT_URI)}"
        "&scope=repo%20read:org%20write:repo_hook%20admin:repo_hook"
    )
    return redirect(github_authorize_url)

# Step 2: Handle GitHub OAuth callback and get the access token
@github_oauth_blueprint.route('/auth/github/callback', methods=['GET'])
@swag_from({
    'tags': ['OAuth'],
    'summary': 'Handle GitHub OAuth callback',
    'description': 'Process GitHub OAuth callback and exchange authorization code for access token',
    'parameters': [
        {
            'name': 'code',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Authorization code from GitHub OAuth'
        },
        {
            'name': 'state',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'State parameter for CSRF protection'
        }
    ],
    'responses': {
        200: {
            'description': 'GitHub authentication successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {'type': 'string', 'example': 'ghp_1234567890abcdef'},
                    'message': {'type': 'string', 'example': 'GitHub authentication successful'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'login': {'type': 'string', 'example': 'username'},
                            'id': {'type': 'integer', 'example': 12345},
                            'avatar_url': {'type': 'string'},
                            'name': {'type': 'string', 'example': 'John Doe'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Authentication failed or missing authorization code',
            'schema': error_response
        }
    }
})
def github_callback():
    # GitHub OAuth flow variables
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Authorization code not provided"}), 400

    # Exchange authorization code for access token
    token_url = "https://github.com/login/oauth/access_token"
    token_data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': GITHUB_REDIRECT_URI,
    }
    headers = {'Accept': 'application/json'}

    token_response = requests.post(token_url, data=token_data, headers=headers)
    token_json = token_response.json()

    if 'access_token' in token_json:
        access_token = token_json['access_token']
        # Send the token to frontend
        return jsonify({
            'access_token': access_token,
            'message': 'GitHub authentication successful',
            'user': user_data
        })
    else:
        return jsonify({'message': 'GitHub authentication failed'}), 400


# Example: Fetch authenticated user's GitHub repositories
@github_oauth_blueprint.route('/auth/github/repos', methods=['GET'])
@swag_from({
    'tags': ['OAuth'],
    'summary': 'Get user GitHub repositories',
    'description': 'Fetch all repositories accessible to the authenticated GitHub user for security scanning',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        }
    ],
    'responses': {
        200: {
            'description': 'Repositories retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 123456},
                        'name': {'type': 'string', 'example': 'my-project'},
                        'full_name': {'type': 'string', 'example': 'username/my-project'},
                        'clone_url': {'type': 'string', 'example': 'https://github.com/username/my-project.git'},
                        'ssh_url': {'type': 'string', 'example': 'git@github.com:username/my-project.git'},
                        'html_url': {'type': 'string', 'example': 'https://github.com/username/my-project'},
                        'private': {'type': 'boolean', 'example': False},
                        'language': {'type': 'string', 'example': 'Python'},
                        'description': {'type': 'string', 'example': 'A sample project'},
                        'updated_at': {'type': 'string', 'format': 'date-time'},
                        'pushed_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        401: {
            'description': 'User not authenticated or invalid GitHub token',
            'schema': error_response
        },
        403: {
            'description': 'GitHub API rate limit exceeded',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_github_repos():
    access_token = session.get('github_access_token')
    if not access_token:
        return jsonify({"error": "User not authenticated"}), 401

    # Fetch user repositories using GitHub API
    repos_url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(repos_url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch repositories"}), response.status_code

    return jsonify(response.json())
