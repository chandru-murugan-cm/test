# CyberSecurity Service API Documentation

This directory contains the API documentation and Swagger/OpenAPI implementation for the CyberSecurity Service.

## Directory Structure

```
docs/
├── README.md                    # This documentation
├── __init__.py                  # Package initialization
└── swagger/
    ├── __init__.py             # Package initialization
    ├── swagger_config.py       # Swagger configuration and setup
    └── swagger_models.py       # API data models and schemas
```

## Quick Start

1. **Access Documentation**: http://localhost:8080/docs/ (when service is running)
2. **API Specification**: http://localhost:8080/apispec.json

## Adding Documentation

Import and use the decorator on your API endpoints:

```python
from flasgger import swag_from
from docs.swagger.swagger_models import project_model, success_response

@app.route('/api/endpoint', methods=['POST'])
@swag_from({
    'tags': ['Category'],
    'summary': 'Brief description',
    'requestBody': {'schema': project_model},
    'responses': {200: {'schema': success_response}},
    'security': [{'Bearer': []}]
})
def your_endpoint():
    pass
```

## Documentation Coverage

- ✅ Projects API
- ✅ Scans API  
- 🚧 Additional endpoints (can be added as needed)

## Authentication

Use the "Authorize" button in Swagger UI with format: `Bearer <your-jwt-token>`