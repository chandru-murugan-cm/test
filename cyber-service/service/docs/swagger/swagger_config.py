"""
Swagger/OpenAPI configuration for CyberSecurity Service API
"""

from flasgger import Swagger

def init_swagger(app):
    """Initialize Swagger documentation for the Flask app"""
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "CyberSecurity Service API",
            "description": """
# CyberSecurity Service API

A comprehensive cybersecurity management platform providing automated security assessments, 
vulnerability tracking, and compliance reporting across multiple technologies and platforms.

## 🛡️ Features
- **Multi-Scanner Integration**: 20+ security scanners (ZAP, Trivy, Slither, Cloudsploit)
- **Comprehensive Coverage**: Web apps, repositories, cloud infrastructure, smart contracts  
- **Compliance Frameworks**: SAMM, ASVS, OWASP Top 10, PCI DSS, HIPAA, GDPR
- **Automated Scheduling**: Continuous security monitoring and assessment

## 🔐 Authentication
All endpoints require JWT Bearer token authentication. Use the **Authorize** button above to configure your token.

## 📚 API Categories

### Core Operations
- **Projects**: Manage security assessment projects and organization
- **Scans**: Execute and monitor security scans across different targets
- **Scanners**: Configure and manage security scanner integrations
- **Scheduler**: Set up automated scan schedules for continuous monitoring

### Findings & Analysis  
- **Findings**: Manage security vulnerabilities and issues discovered
- **Compliance**: Access compliance framework assessments and reporting
- **Scanner Types**: Configure scanner types and target mappings

### Integration & Auth
- **OAuth**: GitHub/GitLab repository access and authentication
- **Targets**: Configure scan targets (domains, repositories, cloud infrastructure)

---
**CyberSecurity Platform** - Advanced Security Management & Compliance
            """,
            "version": "1.0.0",
            "contact": {
                "name": "CyberSecurity Team",
                "email": "support@cybersecurity.com"
            },
            "license": {
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0"
            }
        },
        "host": "localhost:8080",
        "basePath": "/",
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
            },
            "SchedulerSecret": {
                "type": "apiKey",
                "name": "X-Scheduler-Secret",
                "in": "header",
                "description": "Secret key for scheduled scan webhook endpoints"
            }
        },
        "security": [
            {"Bearer": []}
        ],
        "tags": [
            {
                "name": "Projects",
                "description": "🏗️ Project management and organization operations"
            },
            {
                "name": "Scans",
                "description": "🔍 Security scan execution and monitoring operations"
            },
            {
                "name": "Scanners",
                "description": "⚙️ Scanner configuration and management operations"
            },
            {
                "name": "Scanner Types",
                "description": "🔧 Scanner type definitions and target mappings"
            },
            {
                "name": "Scheduler",
                "description": "⏰ Automated scan scheduling and management"
            },
            {
                "name": "Targets",
                "description": "🎯 Scan target configuration and setup"
            },
            {
                "name": "Findings",
                "description": "🚨 Security vulnerability and finding management"
            },
            {
                "name": "Compliance",
                "description": "📋 Compliance assessment and reporting operations"
            },
            {
                "name": "OAuth",
                "description": "🔑 OAuth authentication and repository integration"
            }
        ]
    }

    return Swagger(app, config=swagger_config, template=swagger_template)