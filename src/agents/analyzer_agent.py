"""Analyzer Agent - Analyzes API test requirements and designs test structure."""

from crewai import Agent, LLM

from src.config.settings import get_settings


def create_analyzer_agent() -> Agent:
    """Create the Analyzer Agent that designs API test architecture.
    
    This agent is responsible for:
    - Analyzing parsed API test scenarios
    - Identifying authentication requirements (OAuth2, Basic Auth, API Keys)
    - Designing request payload structures
    - Mapping assertions to response validations
    - Identifying edge cases and boundary conditions
    """
    settings = get_settings()
    
    llm = LLM(
        model=settings.ollama.get_model_string(),
        base_url=settings.ollama.base_url,
        temperature=settings.ollama.temperature,
    )
    
    return Agent(
        role="API Test Architect & Analyzer",
        goal="""Analyze parsed API test scenarios and create a detailed test 
        blueprint with specific authentication flows, request configurations, 
        payload structures, and response assertions needed to implement 
        comprehensive API test cases.""",
        backstory="""You are a senior API test automation architect with deep 
        expertise in RESTful API testing. You have extensive experience with 
        authentication mechanisms (OAuth2, JWT, Basic Auth, API Keys), HTTP 
        protocols, and API testing frameworks like pytest with requests. You 
        understand best practices for API testing including proper assertion 
        strategies, error handling, SSL/TLS configurations, and test data 
        management. You know how to design tests that validate status codes, 
        response bodies, headers, and error messages.""",
        llm=llm,
        verbose=settings.verbose,
        allow_delegation=False,
        memory=True,
    )


# Analysis guidelines for the agent
ANALYZER_GUIDELINES = """
## API Test Analysis Best Practices

### Authentication Analysis
1. OAuth2 Token Flow:
   - Token endpoint URL
   - Client credentials or user credentials
   - Token request payload (grant_type, scope)
   - Token extraction from response
   - Bearer token header format

2. Basic Auth:
   - Username/password encoding
   - Authorization header format

3. API Key:
   - Header name (X-API-Key, Authorization)
   - Key value handling

### Request Configuration

| Component | Analysis Points |
|-----------|-----------------|
| Method | GET, POST, PUT, DELETE, PATCH |
| Headers | Content-Type, Accept, Authorization |
| Payload | JSON structure, required fields, data types |
| URL Params | Query parameters, path parameters |

### Assertion Mapping

Map expected outcomes to API assertions:

| Expected Outcome | Python Assertion |
|-----------------|------------------|
| Status 200/201 | `assert response.status_code in [200, 201]` |
| JSON response | `response.json()` |
| Field exists | `assert "field" in response.json()` |
| Field value | `assert response.json()["field"] == expected` |
| Error message | `assert "error" in response.json()` |

### Test Blueprint Structure

```json
{
  "class_name": "TestCreatePolicyAPI",
  "test_name": "test_create_policy_with_valid_description",
  "auth_config": {
    "type": "oauth2",
    "token_url": "https://...",
    "credentials": {"username": "...", "password": "..."},
    "token_payload": {"grant_type": "client_credentials", "scope": "full"}
  },
  "request_config": {
    "method": "POST",
    "endpoint": "/policies",
    "headers": {"Content-Type": "application/json"},
    "payload": {...}
  },
  "assertions": [
    {"type": "status_code", "expected": [200, 201]},
    {"type": "json_field", "field": "policyId", "condition": "exists"}
  ],
  "ssl_verify": false
}
```
"""
