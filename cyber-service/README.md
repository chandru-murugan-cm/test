# CyberSecurity Service

A comprehensive Flask-based REST API service for security scanning and compliance management. This service provides automated security assessments, vulnerability tracking, and compliance reporting across multiple platforms and technologies.

## Features

- **Multi-Scanner Integration**: Support for 20+ security scanners (ZAP, Trivy, Slither, Cloudsploit, Wapiti, Gitleaks)
- **Target Diversity**: Scan web applications, repositories, cloud infrastructure, and smart contracts
- **Compliance Frameworks**: Built-in support for SAMM, ASVS, OWASP Top 10, PCI DSS, HIPAA, GDPR
- **Interactive API Documentation**: Comprehensive Swagger/OpenAPI documentation with testing capabilities
- **Authentication & Authorization**: JWT-based security with user data scoping
- **Scheduling System**: Automated scan scheduling with Google Cloud Scheduler integration
- **Containerized Deployment**: Docker Compose setup for easy development and deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)

### Using Docker (Recommended)

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Access the API documentation**:
   - Swagger UI: http://localhost:8080/docs/
   - API Specification: http://localhost:8080/apispec.json

3. **Stop the services**:
   ```bash
   docker-compose down
   ```

### Local Development

1. **Navigate to service directory**:
   ```bash
   cd service/
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.dev .env
   # Edit .env with your MongoDB connection string
   ```

5. **Run the service**:
   ```bash
   python app.py
   ```

## API Documentation

### Swagger UI
Interactive API documentation is available at `/docs/` when the service is running. The Swagger UI provides:

- **Complete API Reference**: All endpoints with request/response schemas
- **Interactive Testing**: Test API endpoints directly from the browser
- **Authentication Integration**: Built-in JWT token management
- **Request Examples**: Sample requests and responses for all operations

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/crscan/project` | GET, POST, PUT, DELETE | Project management |
| `/cs/scans` | GET, POST | Security scan operations |
| `/cs/scanners` | GET, POST | Scanner configuration |
| `/cs/scanner-types` | GET | Available scan types |
| `/crscan/domain` | GET, POST | Domain target management |
| `/crscan/repository` | GET, POST | Repository target management |
| `/crscan/finding_master/{project_id}` | GET | Security findings |
| `/cs/scheduler` | GET, POST, PUT, DELETE | Scan scheduling |

### Authentication

All API endpoints (except OAuth) require JWT Bearer token authentication:

```bash
Authorization: Bearer <your-jwt-token>
```

Use the "Authorize" button in Swagger UI to configure authentication for testing.

## Architecture

### Service Components

- **Flask Application**: Core REST API service
- **MongoDB Database**: Data persistence and document storage
- **Scanner Integrations**: Modular scanner implementations
- **Scheduler Service**: Automated scan execution
- **OAuth Integration**: GitHub/GitLab repository access

### Project Structure

```
service/
├── app.py                      # Main Flask application
├── docs/                       # API documentation
│   ├── swagger/               # Swagger configuration
│   │   ├── swagger_config.py  # Swagger setup
│   │   └── swagger_models.py  # API schemas
│   ├── README.md              # Documentation guide
│   └── DOCKER_SETUP.md        # Docker instructions
├── apis/                       # REST API endpoints
├── controllers/                # Business logic layer
├── entities/                   # Database models
├── requirements.txt            # Python dependencies
└── Dockerfile                  # Container configuration
```

### Database Schema

The service uses MongoDB with the following key collections:

- **Projects**: Security assessment projects
- **Scans**: Scan execution records and status
- **Findings**: Security vulnerabilities and issues
- **Scanners**: Scanner configurations and capabilities
- **ScannerTypes**: Available scan types and target mappings
- **Schedules**: Automated scan schedules

## Scanner Integration

### Supported Scanners

| Scanner | Type | Targets | Description |
|---------|------|---------|-------------|
| **OWASP ZAP** | DAST | Web Applications | Web application security testing |
| **Trivy** | SCA/SAST | Repositories | Vulnerability and license scanning |
| **Slither** | SAST | Smart Contracts | Solidity security analysis |
| **Cloudsploit** | CSPM | Cloud Infrastructure | AWS/Azure/GCP security assessment |
| **Wapiti** | DAST | Web Applications | Web vulnerability scanner |
| **Gitleaks** | SAST | Repositories | Secret detection in source code |

### Adding Custom Scanners

1. Create scanner implementation in `controllers/utility/`
2. Define scanner configuration in database
3. Add endpoint documentation in respective API file
4. Update scanner type mappings

## Testing

This project maintains **100% test coverage** with comprehensive unit and integration tests.

### Test Architecture

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── __init__.py                    # Test package initialization
├── unit/                          # Unit tests (100% coverage)
│   ├── controllers/               # Controller logic tests
│   │   ├── test_ProjectController.py
│   │   ├── test_ScannersController.py
│   │   ├── test_ScansController.py
│   │   ├── test_SchedulerController.py
│   │   ├── test_DomainController.py
│   │   └── test_RepositoryController.py
│   ├── apis/                      # API endpoint tests
│   │   ├── test_project.py
│   │   ├── test_scanners.py
│   │   └── test_scans.py
│   └── entities/                  # Entity/model tests
└── integration/                   # Integration tests
    ├── workflows/                 # End-to-end workflow tests
    │   └── test_scanning_workflow.py
    ├── api_integration/           # Cross-API integration tests
    ├── external_services/         # External service integration tests
    └── database/                  # Database integration tests
```

### Running Tests

#### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov mongomock flask-testing

# Or install all dependencies
pip install -r requirements.txt
```

#### Execute Tests

**Run all tests:**
```bash
# From service directory
cd service/
pytest

# With coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing
```

**Run specific test categories:**
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only  
pytest tests/integration/

# Specific test file
pytest tests/unit/controllers/test_ProjectController.py

# Specific test method
pytest tests/unit/controllers/test_ProjectController.py::TestProjectController::test_add_entity_success
```

**Run tests with verbose output:**
```bash
pytest -v --tb=short
```

### Test Features

#### Comprehensive Coverage
- **Unit Tests**: All controllers, APIs, and utilities with 100% line coverage
- **Integration Tests**: Complete workflow testing from API to database
- **Error Handling**: All error scenarios and edge cases covered
- **Authentication**: JWT token validation and user authorization testing
- **Database Integration**: MongoDB operations with mongomock for isolation

#### Advanced Testing Patterns
- **Mocking Strategy**: Extensive use of unittest.mock for isolation
- **Fixtures**: Reusable test data and setup via pytest fixtures
- **Parameterized Tests**: Data-driven testing for multiple scenarios
- **Concurrent Testing**: Thread safety and concurrent request handling
- **Performance Testing**: Response time and resource usage validation

#### Test Data Management
```python
# Sample fixtures available in conftest.py
@pytest.fixture
def sample_project_data():
    return {
        'name': 'Test Security Project',
        'description': 'A test project for security assessments',
        'owner': 'test-user@example.com',
        'project_type': 'web_application',
        'status': 'active'
    }

@pytest.fixture
def mock_db():
    """Mock MongoDB connection for tests."""
    connect('mongoenginetest', host='mongomock://localhost')
    yield
    disconnect()
```

#### Mock External Services
All external dependencies are mocked for reliable testing:
- **MongoDB**: Using mongomock for database operations
- **JWT Authentication**: Mocked token validation
- **Scanner Tools**: Mocked scanner execution and responses
- **Cloud Services**: Mocked Google Cloud Scheduler and Azure/AWS APIs
- **OpenAI API**: Mocked GPT responses for smart contract analysis

### Continuous Integration

Tests are designed to run in CI/CD environments with:
- **Fast Execution**: Tests complete in under 30 seconds
- **Isolated Environment**: No external dependencies required
- **Deterministic Results**: Consistent outcomes across environments
- **Comprehensive Reporting**: Coverage reports and test result summaries

### Test Development Guidelines

When adding new features:

1. **Write Tests First**: Follow TDD principles
2. **Maintain Coverage**: Ensure 100% line coverage for new code
3. **Test Error Cases**: Include negative testing scenarios
4. **Use Proper Mocking**: Isolate units under test
5. **Integration Testing**: Add workflow tests for new API endpoints

## Configuration

### Environment Variables

Key configuration options (set in `.env` or Docker environment):

```bash
# Database
DATABASE_CONNECTION_STRING=mongodb://localhost:27017/scans_db
DATABASE_NAME=scans_db
TESTING=False                      # Set to True for test environment

# Security
JWTSECRET=your-jwt-secret-key

# External Services
OPENAI_API_KEY=your-openai-key
SCHEDULER_SECRET_KEY=your-scheduler-secret

# Flask Configuration
FLASK_ENV=development

# Testing Configuration
DATABASE_NAME_TEST=test_scans_db   # Test database name
```

### Docker Configuration

The `docker-compose.yaml` file defines:

- **cyber-service**: Main Flask application container
- **mongodb_container**: MongoDB database container
- **Networking**: Internal container communication
- **Persistence**: MongoDB data volume

## Development

### Adding New Endpoints

1. **Create API endpoint** in `apis/` directory
2. **Add controller logic** in `controllers/`
3. **Define database models** in `entities/`
4. **Add Swagger documentation**:
   ```python
   from flasgger import swag_from
   from docs.swagger.swagger_models import success_response

   @swag_from({
       'tags': ['Category'],
       'summary': 'Endpoint description',
       'responses': {200: {'schema': success_response}},
       'security': [{'Bearer': []}]
   })
   ```

### Running Tests

```bash
# Unit tests
python -m unittest discover tests/

# Integration tests
pytest tests/
```

### Code Quality

The project follows Python best practices:

- **PEP 8**: Code style compliance
- **Type Hints**: Function and variable typing
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Structured exception management
- **Security**: Input validation and sanitization

## Deployment

### Docker Deployment

1. **Build and run**:
   ```bash
   docker-compose up -d
   ```

2. **Complete Docker cleanup** (if needed):
   ```bash
   # One-liner complete cleanup
   docker-compose down && docker system prune -a --volumes --force && docker buildx prune --all --force
   
   # Then rebuild and test
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Scale services** (if needed):
   ```bash
   docker-compose up --scale cyber-service=3
   ```

4. **Monitor logs**:
   ```bash
   docker-compose logs -f
   ```

### Production Considerations

- **Environment Variables**: Use secure secret management
- **Database**: Configure MongoDB replica sets for high availability
- **Load Balancing**: Deploy behind reverse proxy (nginx/Apache)
- **SSL/TLS**: Enable HTTPS for production deployments
- **Monitoring**: Implement logging and monitoring solutions

## Compliance & Security

### Security Features

- **JWT Authentication**: Secure token-based authentication
- **Data Scoping**: Users can only access their own data
- **Input Validation**: Comprehensive request validation
- **SQL Injection Prevention**: Parameterized database queries
- **Soft Delete**: Data retention for audit trails

### Compliance Support

- **SAMM**: Software Assurance Maturity Model
- **ASVS**: Application Security Verification Standard
- **OWASP Top 10**: Web application security risks
- **PCI DSS**: Payment card industry standards
- **HIPAA**: Healthcare data protection
- **GDPR**: General data protection regulation

## Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Follow code standards**: Maintain existing code style and patterns
4. **Add tests**: Include unit tests for new functionality
5. **Update documentation**: Add Swagger documentation for new endpoints
6. **Submit pull request**: Include detailed description of changes

### Development Guidelines

- **Code Review**: All changes require peer review
- **Testing**: Maintain test coverage above 80%
- **Documentation**: Update API documentation for all changes
- **Security**: Follow secure coding practices
- **Performance**: Consider performance impact of changes

## Support

- **Documentation**: `/docs/` endpoint when service is running
- **API Reference**: Swagger UI at `/docs/`
- **Issues**: Use GitHub issues for bug reports and feature requests
- **Contributions**: Follow contributing guidelines for pull requests

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.